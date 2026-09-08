#!/usr/bin/env python3
"""Fetch Steam metadata, optionally ask Gemini for new dossiers, then rebuild docs/.

Seed (no API key): python scripts/fetch_and_summarize.py --seed
Daily update:      python scripts/fetch_and_summarize.py --update --max 3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from gemini_prompt import (  # noqa: E402
    DOSSIER_SCHEMA,
    GEMINI_MODEL_DEFAULT,
    GEMINI_MODEL_FALLBACKS,
    SYSTEM_PROMPT,
    repair_prompt,
    user_prompt,
)
from build_site import build, load_dotenv, load_seed_games, normalize_game, steam_urls  # noqa: E402

STEAM_DETAILS = "https://store.steampowered.com/api/appdetails"
STEAM_REVIEWS = "https://store.steampowered.com/appreviews/{appid}"
GEMINI_GENERATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODELS = "https://generativelanguage.googleapis.com/v1beta/models"
HEADERS = {
    "User-Agent": "J-IndieRadar/1.0 (editorial static site builder; +https://github.com/)",
}

LEVELS = {
    "None (Visual/Action only)": 0,
    "Low (Basic UI/Menu)": 1,
    "Medium (Screen Translation OK)": 2,
    "High (Text-Heavy/Lore)": 3,
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sleep_between_calls() -> None:
    time.sleep(8)


def fetch_steam_details(appid: int, session: requests.Session) -> dict | None:
    try:
        res = session.get(
            STEAM_DETAILS,
            params={"appids": appid, "l": "english", "cc": "us"},
            timeout=30,
            headers=HEADERS,
        )
        res.raise_for_status()
        blob = res.json().get(str(appid), {})
        if not blob.get("success"):
            return None
        return blob.get("data") or {}
    except Exception as exc:
        print(f"[steam] details failed for {appid}: {exc}")
        return None


def fetch_japanese_reviews(appid: int, session: requests.Session, count: int = 25) -> str:
    try:
        res = session.get(
            STEAM_REVIEWS.format(appid=appid),
            params={
                "json": 1,
                "language": "japanese",
                "filter": "recent",
                "num_per_page": min(count, 30),
                "purchase_type": "all",
            },
            timeout=30,
            headers=HEADERS,
        )
        res.raise_for_status()
        reviews = res.json().get("reviews") or []
        snippets = []
        for item in reviews[:count]:
            text = re.sub(r"\s+", " ", (item.get("review") or "")).strip()
            if len(text) > 400:
                text = text[:400] + "..."
            if text:
                snippets.append(f"- {text}")
        return "\n".join(snippets) if snippets else "(no Japanese reviews returned)"
    except Exception as exc:
        print(f"[steam] reviews failed for {appid}: {exc}")
        return "(review fetch failed)"


def _norm_name(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split())


def names_match(expected: str, steam_name: str) -> bool:
    """Steam recycles app IDs. Never treat a recycled store page as the same game."""
    left = _norm_name(expected)
    right = _norm_name(steam_name)
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    stop = {"the", "of", "and", "a", "an", "in", "to"}
    left_tokens = set(left.split()) - stop
    right_tokens = set(right.split()) - stop
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    return overlap >= 2 and overlap / min(len(left_tokens), len(right_tokens)) >= 0.5


def enrich_from_steam(game: dict, details: dict | None) -> dict:
    out = dict(game)
    if out.get("skip_steam"):
        return out
    appid = int(out["appid"])
    urls = steam_urls(appid)
    expected = str(out.get("title") or "")
    steam_name = str((details or {}).get("name") or "")
    if expected and steam_name and not names_match(expected, steam_name):
        print(
            f"[steam] appid {appid} is now {steam_name!r}, not {expected!r}; "
            "keeping editorial title and skipping store artwork"
        )
        out["steam_mismatch"] = True
        return out
    if not details:
        if not expected:
            out.setdefault("header_image", urls["header_image"])
            out.setdefault("steam_url", urls["steam_url"])
        return out
    out["steam_url"] = urls["steam_url"]
    if not out.get("title"):
        out["title"] = steam_name or f"App {appid}"
    devs = details.get("developers") or []
    if devs and not out.get("developer"):
        out["developer"] = ", ".join(devs)
    release = (details.get("release_date") or {}).get("date") or ""
    year = re.search(r"(19|20)\d{2}", release)
    if year and not out.get("release_year"):
        out["release_year"] = int(year.group(0))
    header = details.get("header_image")
    if header:
        out["header_image"] = header
    else:
        out.setdefault("header_image", urls["header_image"])
    genres = [g.get("description") for g in details.get("genres") or [] if g.get("description")]
    if genres and not out.get("genres"):
        out["genres"] = genres[:4]
    if not out.get("primary_genre") and out.get("genres"):
        out["primary_genre"] = out["genres"][0]
    return out


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text or ""))


def coerce_language_level(raw: str) -> str:
    text = (raw or "").strip()
    if text in LEVELS:
        return text
    low = text.lower()
    if "none" in low or "visual" in low:
        return "None (Visual/Action only)"
    if low.startswith("low") or "basic ui" in low:
        return "Low (Basic UI/Menu)"
    if low.startswith("high") or "text-heavy" in low or "lore" in low:
        return "High (Text-Heavy/Lore)"
    if low.startswith("medium") or "screen" in low:
        return "Medium (Screen Translation OK)"
    return "Medium (Screen Translation OK)"


def coerce_dossier(payload: dict) -> dict:
    out = dict(payload)
    why = out.get("why_trending_in_japan")
    if isinstance(why, list):
        fixed = []
        for item in why:
            if isinstance(item, str) and item.strip():
                heading, _, rest = item.partition(".")
                fixed.append({"title": heading.strip() or item[:80], "details": (rest or item).strip()})
            elif isinstance(item, dict):
                title = str(item.get("title") or "").strip()
                details = str(item.get("details") or "").strip()
                if title or details:
                    fixed.append({"title": title or (details[:80] if details else "Note"), "details": details or title})
        out["why_trending_in_japan"] = fixed[:3]
    lb = out.get("language_barrier")
    if isinstance(lb, str):
        out["language_barrier"] = {"level": coerce_language_level(lb), "details": lb}
    elif isinstance(lb, dict):
        fixed_lb = dict(lb)
        fixed_lb["level"] = coerce_language_level(str(fixed_lb.get("level") or ""))
        if not str(fixed_lb.get("details") or "").strip():
            fixed_lb["details"] = str(lb.get("level") or "See language notes in the dossier.")
        out["language_barrier"] = fixed_lb
    return out


def validate_dossier(payload: dict, strict: bool = True) -> list[str]:
    errors = []
    for key in ("vibe", "what_is_it", "deep_dive_analysis", "playtime_and_difficulty", "target_audience"):
        if not str(payload.get(key, "")).strip():
            errors.append(f"missing {key}")
    what = word_count(payload.get("what_is_it", ""))
    what_min, what_max = (120, 260) if strict else (80, 400)
    if what < what_min or what > what_max:
        errors.append(f"what_is_it word count {what} not in 150-200 (±slack)")
    deep = word_count(payload.get("deep_dive_analysis", ""))
    deep_min = 180 if strict else 120
    if deep < deep_min:
        errors.append(f"deep_dive_analysis word count {deep} < 200")
    why = payload.get("why_trending_in_japan")
    if not isinstance(why, list) or len(why) != 3:
        errors.append("why_trending_in_japan must have 3 items")
    else:
        for idx, item in enumerate(why):
            if not isinstance(item, dict) or not str(item.get("title", "")).strip() or not str(item.get("details", "")).strip():
                errors.append(f"why_trending_in_japan[{idx}] needs title and details")
    lb = payload.get("language_barrier") or {}
    if not isinstance(lb, dict) or lb.get("level") not in LEVELS:
        errors.append("language_barrier.level invalid")
    elif not str(lb.get("details", "")).strip():
        errors.append("language_barrier.details missing")
    return errors


def extract_json(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Gemini response was empty")
    candidates = [text]
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fence:
        candidates.insert(0, fence.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(text[start : end + 1])
    last_error: Exception | None = None
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(payload, dict):
            return payload
        last_error = ValueError("JSON root was not an object")
    raise ValueError(f"Gemini response was not JSON ({last_error})")


class ModelUnavailable(RuntimeError):
    """The requested Gemini model alias does not exist for this API key."""


def gemini_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_"):
        raise RuntimeError("GEMINI_API_KEY is not set")
    return api_key


def gemini_headers(api_key: str) -> dict[str, str]:
    return {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
        "User-Agent": HEADERS["User-Agent"],
    }


def model_candidates() -> list[str]:
    preferred = (os.environ.get("GEMINI_MODEL") or GEMINI_MODEL_DEFAULT).strip()
    names: list[str] = []
    for name in [preferred, *GEMINI_MODEL_FALLBACKS]:
        cleaned = (name or "").removeprefix("models/").strip()
        if cleaned and cleaned not in names:
            names.append(cleaned)
    return names


def discover_flash_models(api_key: str) -> list[str]:
    try:
        res = requests.get(GEMINI_MODELS, headers=gemini_headers(api_key), timeout=30)
        res.raise_for_status()
        models = res.json().get("models") or []
    except Exception as exc:
        print(f"[gemini] could not list models: {exc}")
        return []
    skip = ("embed", "image", "tts", "audio", "robotics", "computer-use", "native-audio")
    found: list[str] = []
    for item in models:
        methods = item.get("supportedGenerationMethods") or []
        if "generateContent" not in methods:
            continue
        name = str(item.get("name") or "").removeprefix("models/")
        low = name.lower()
        if "flash" not in low or any(token in low for token in skip):
            continue
        found.append(name)
    rank = ("3.6-flash", "3.5-flash", "3.1-flash", "flash-latest", "2.5-flash")
    found.sort(key=lambda name: next((i for i, token in enumerate(rank) if token in name.lower()), 99))
    if found:
        print("[gemini] discovered models: " + ", ".join(found[:8]))
    return found


def generation_config(thinking: str | None, use_schema: bool) -> dict[str, Any]:
    config: dict[str, Any] = {
        "responseMimeType": "application/json",
        "maxOutputTokens": 8192,
    }
    if use_schema:
        config["responseSchema"] = DOSSIER_SCHEMA
    if thinking == "minimal":
        config["thinkingConfig"] = {"thinkingLevel": "minimal"}
    elif thinking == "MINIMAL":
        config["thinkingConfig"] = {"thinkingLevel": "MINIMAL"}
    elif thinking == "budget":
        config["thinkingConfig"] = {"thinkingBudget": 0}
    return config


def collect_gemini_text(payload: dict) -> str:
    feedback = payload.get("promptFeedback") or {}
    if feedback.get("blockReason"):
        raise ValueError(f"Gemini blocked the prompt ({feedback.get('blockReason')})")
    error = payload.get("error") or {}
    if error:
        raise ValueError(error.get("message") or str(error))
    candidates = payload.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini returned no candidates")
    candidate = candidates[0]
    finish = candidate.get("finishReason")
    parts = ((candidate.get("content") or {}).get("parts")) or []
    texts: list[str] = []
    for part in parts:
        if part.get("thought"):
            continue
        text = part.get("text")
        if text:
            texts.append(str(text))
    joined = "".join(texts).strip()
    if not joined:
        raise ValueError(f"Gemini response had no text (finishReason={finish})")
    if finish in {"SAFETY", "RECITATION", "PROHIBITED_CONTENT", "BLOCKLIST"}:
        raise ValueError(f"Gemini stopped for {finish}")
    return joined


def post_gemini(api_key: str, model_name: str, prompt: str, thinking: str | None, use_schema: bool) -> str:
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config(thinking, use_schema),
    }
    url = GEMINI_GENERATE.format(model=model_name)
    res = requests.post(url, headers=gemini_headers(api_key), json=body, timeout=180)
    snippet = (res.text or "")[:500]
    if res.status_code == 404:
        raise ModelUnavailable(snippet)
    if res.status_code in (401, 403):
        raise RuntimeError(f"Gemini auth failed ({res.status_code}): {snippet}")
    if res.status_code == 429:
        raise RetryableHttpError(snippet)
    if res.status_code == 400:
        raise BadRequestError(snippet)
    if res.status_code >= 400:
        raise RetryableHttpError(f"HTTP {res.status_code}: {snippet}")
    return collect_gemini_text(res.json())


class RetryableHttpError(RuntimeError):
    pass


class BadRequestError(RuntimeError):
    pass


def generate_with_model(api_key: str, model_name: str, prompt: str, config_state: list[Any]) -> str:
    thinking, use_schema = config_state
    last_error: Exception | None = None
    tried: set[tuple[str | None, bool]] = set()
    while True:
        key = (thinking, use_schema)
        if key in tried:
            break
        tried.add(key)
        try:
            return post_gemini(api_key, model_name, prompt, thinking, use_schema)
        except ModelUnavailable:
            raise
        except BadRequestError as exc:
            last_error = exc
            message = str(exc).lower()
            print(f"[gemini] {model_name} rejected config thinking={thinking} schema={use_schema}")
            if thinking and ("thinking" in message or "budget" in message or "level" in message):
                if thinking == "minimal":
                    thinking, config_state[0] = "MINIMAL", "MINIMAL"
                    continue
                if thinking == "MINIMAL":
                    thinking, config_state[0] = "budget", "budget"
                    continue
                thinking, config_state[0] = None, None
                continue
            if use_schema and "schema" in message:
                use_schema, config_state[1] = False, False
                continue
            if thinking is not None:
                thinking, config_state[0] = None, None
                continue
            if use_schema:
                use_schema, config_state[1] = False, False
                continue
            raise
    raise last_error or RuntimeError("Gemini rejected all request configs")


def call_gemini(meta: dict, reviews: str) -> dict:
    api_key = gemini_api_key()
    prompt = user_prompt(meta, reviews)
    last_error: Exception | None = None
    config_state: list[Any] = ["minimal", True]
    names = model_candidates()
    seen: set[str] = set()
    discovered = False
    idx = 0
    while idx < len(names):
        model_name = names[idx]
        idx += 1
        if model_name in seen:
            continue
        seen.add(model_name)
        print(f"[gemini] trying {model_name}")
        draft: dict | None = None
        errors: list[str] = ["response was not JSON"]
        for attempt in range(5):
            try:
                if attempt:
                    sleep_between_calls()
                to_send = prompt if draft is None else repair_prompt(draft, errors)
                text = generate_with_model(api_key, model_name, to_send, config_state)
                try:
                    draft = coerce_dossier(extract_json(text))
                except ValueError:
                    draft = {"_raw": text[:5000]}
                    raise
                errors = validate_dossier(draft, strict=attempt < 4)
                if errors:
                    raise ValueError("; ".join(errors))
                return draft
            except ModelUnavailable as exc:
                last_error = exc
                print(f"[gemini] {model_name} unavailable ({exc})")
                if not discovered:
                    for extra in discover_flash_models(api_key):
                        if extra not in seen and extra not in names:
                            names.append(extra)
                    discovered = True
                break
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                print(f"[gemini] {model_name} attempt {attempt + 1} failed ({exc})")
                if "auth failed" in message:
                    raise
                retryable = any(
                    token in message
                    for token in (
                        "429",
                        "resource exhausted",
                        "quota",
                        "overloaded",
                        "word count",
                        "not json",
                        "missing ",
                        "must have",
                        "invalid",
                        "empty",
                        "no text",
                        "no candidates",
                        "http 5",
                    )
                )
                if not retryable:
                    break
                time.sleep(min(60, 8 * (2 ** attempt)))
    raise RuntimeError(f"Gemini failed after retries: {last_error}")


def slugify(title: str, appid: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or f"app-{appid}"


def dossier_from_gemini(appid: int, session: requests.Session) -> dict:
    details = fetch_steam_details(appid, session)
    if not details:
        raise RuntimeError(f"Steam returned no details for {appid}")
    if (details.get("type") or "game") != "game":
        raise RuntimeError(f"Steam app {appid} is {details.get('type')}, not a game")
    reviews = fetch_japanese_reviews(appid, session)
    name = details.get("name") or f"Steam app {appid}"
    developers = ", ".join(details.get("developers") or ["Unknown"])
    genres = [g.get("description") for g in details.get("genres") or [] if g.get("description")]
    cats = [c.get("description") for c in details.get("categories") or [] if c.get("description")]
    tags = ", ".join(genres + cats[:8])
    languages = details.get("supported_languages") or ""
    short = re.sub("<[^<]+?>", "", details.get("short_description") or "")
    release = details.get("release_date") or {}
    year_match = re.search(r"(19|20)\d{2}", release.get("date") or "")
    meta = {
        "title": name,
        "developer": developers,
        "release_year": int(year_match.group(0)) if year_match else date.today().year,
        "tags": tags,
        "languages": languages,
        "short_description": short,
    }
    generated = call_gemini(meta, reviews)
    lb = generated["language_barrier"]
    lb["score"] = LEVELS.get(lb["level"], 2)
    primary = "Action"
    joined = " ".join(genres).lower()
    if "rpg" in joined:
        primary = "JRPG"
    elif "horror" in joined:
        primary = "Horror"
    elif "rogue" in joined:
        primary = "Roguelite"
    elif "adventure" in joined:
        primary = "Adventure"
    playtime_short = generated["playtime_and_difficulty"].split(".")[0][:48]
    urls = steam_urls(appid)
    game = {
        "appid": appid,
        "slug": slugify(name, appid),
        "title": name,
        "developer": developers,
        "release_year": meta["release_year"],
        "genres": genres[:4] or [primary],
        "primary_genre": primary,
        "vibe": generated["vibe"],
        "playtime_short": playtime_short,
        "difficulty": playtime_short,
        "language_barrier": lb,
        "what_is_it": generated["what_is_it"],
        "deep_dive_analysis": generated["deep_dive_analysis"],
        "why_trending_in_japan": generated["why_trending_in_japan"],
        "playtime_and_difficulty": generated["playtime_and_difficulty"],
        "target_audience": generated["target_audience"],
        "header_image": details.get("header_image") or urls["header_image"],
        "steam_url": urls["steam_url"],
        "updated": date.today().isoformat(),
        "source": "gemini",
    }
    return normalize_game(game)


def merge_by_appid(existing: list[dict], incoming: list[dict]) -> list[dict]:
    index = {int(g["appid"]): g for g in existing}
    for game in incoming:
        index[int(game["appid"])] = normalize_game(game)
    return list(index.values())


def seed(session: requests.Session) -> list[dict]:
    games = load_seed_games()
    if not games:
        raise SystemExit("No seed JSON found in data/seed/")
    enriched = []
    for game in games:
        if game.get("skip_steam"):
            enriched.append(normalize_game(game))
            continue
        details = fetch_steam_details(int(game["appid"]), session)
        enriched.append(normalize_game(enrich_from_steam(game, details)))
        time.sleep(0.35)
    save_json(DATA / "games.json", enriched)
    print(f"Seeded {len(enriched)} dossiers")
    return enriched


def update(session: requests.Session, max_new: int, only_appids: list[int] | None = None) -> list[dict]:
    gemini_api_key()
    catalog = load_json(DATA / "games.json", [])
    if not catalog:
        catalog = seed(session)
    known = {int(g["appid"]) for g in catalog}
    watch = only_appids if only_appids else load_json(DATA / "watchlist.json", [])
    if only_appids:
        pending = [int(appid) for appid in watch]
    else:
        pending = [int(appid) for appid in watch if int(appid) not in known]
    if not pending:
        print("No new watchlist titles to add. Rebuilding existing catalog.")
        save_json(DATA / "games.json", catalog)
        return catalog
    added = []
    failed: list[tuple[int, str]] = []
    for appid in pending:
        if len(added) >= max_new:
            break
        print(f"[update] generating dossier for {appid}")
        try:
            game = dossier_from_gemini(appid, session)
        except Exception as exc:
            print(f"[update] skipped {appid}: {exc}")
            failed.append((appid, str(exc)))
            continue
        added.append(game)
        known.add(appid)
    if added:
        print(f"[update] added {len(added)} dossier(s)")
    if failed:
        print(f"[update] {len(failed)} failed: " + "; ".join(f"{appid} ({err})" for appid, err in failed))
    if not added:
        raise SystemExit("No new dossiers were generated. Check GEMINI_API_KEY, model name, and watchlist app IDs.")
    merged = merge_by_appid(catalog, added)
    save_json(DATA / "games.json", merged)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Build the 20+ seed dossiers (Steam enrich, no Gemini required)")
    parser.add_argument("--update", action="store_true", help="Add up to N unseen Japanese indies via Gemini")
    parser.add_argument("--max", type=int, default=3, help="Max new games for --update")
    parser.add_argument("--appid", type=int, action="append", help="Generate a dossier for one Steam app ID (repeatable)")
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()

    session = requests.Session()
    if args.build_only:
        build()
        return
    if args.appid:
        update(session, max(1, len(args.appid)), only_appids=args.appid)
        build()
        return
    if args.update:
        update(session, max(1, args.max))
        build()
        return
    # Default and --seed both produce a review-ready site from bundled dossiers.
    seed(session)
    build()


if __name__ == "__main__":
    main()
