#!/usr/bin/env python3
"""Render docs/ from data/games.json and the legal-page copy."""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from jinja2 import BaseLoader, Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from pages import page_defs  # noqa: E402

DOCS = ROOT / "docs"
TEMPLATES = ROOT / "templates"
DATA = ROOT / "data"
SEED_DIR = DATA / "seed"


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def site_config() -> dict:
    load_dotenv()
    site_url = (os.environ.get("SITE_URL") or "https://j-indie-radar.pages.dev").rstrip("/")
    return {
        "site_name": "J-Indie Radar",
        "site_url": site_url,
        "tagline": "Discover Hidden Japanese Indie Gems & Untranslated Classics",
        "contact_email": os.environ.get("CONTACT_EMAIL", "editorial@j-indie-radar.example"),
        "google_form_embed": os.environ.get(
            "GOOGLE_FORM_EMBED_URL",
            "https://docs.google.com/forms/d/e/1FAIpQLSfqzO3DXp5V8f8FdWfNxgAk_bgJMSXIcMlWHQiFvQkuTMMukA/viewform?embedded=true",
        ).strip(),
        "adsense_client_id": os.environ.get("ADSENSE_CLIENT_ID", "ca-pub-2075840815269276").strip() or "ca-pub-2075840815269276",
        "ga_id": os.environ.get("GA_MEASUREMENT_ID", "").strip(),
        "year": date.today().year,
    }


def jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["media_url"] = media_url
    return env


def load_seed_games() -> list[dict]:
    games: list[dict] = []
    if not SEED_DIR.exists():
        return games
    for path in sorted(SEED_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            games.extend(payload)
        elif isinstance(payload, dict):
            games.append(payload)
    return games


def load_catalog() -> list[dict]:
    catalog_path = DATA / "games.json"
    if catalog_path.exists():
        games = json.loads(catalog_path.read_text(encoding="utf-8"))
        if games:
            return games
    return load_seed_games()


def steam_urls(appid: int) -> dict:
    return {
        "header_image": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
        "steam_url": f"https://store.steampowered.com/app/{appid}/",
        "og_fallback": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
    }


def media_url(url: str, root_prefix: str = "") -> str:
    url = (url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if not url:
        url = "img/placeholder-header.svg"
    return f"{root_prefix}{url.lstrip('/')}"


def absolute_media(cfg: dict, url: str) -> str:
    url = (url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if not url:
        url = "img/placeholder-header.svg"
    return f"{cfg['site_url']}/{url.lstrip('/')}"


# Used when a dossier has no explicit featured flag and dates are tied.
DEFAULT_FEATURED_SLUGS = ("cave-story-plus", "yume-nikki")


def _clean_text(value) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:—-") + "…"


def _truncate_chars(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars + 1].rsplit(" ", 1)[0].rstrip(".,;:—-")
    if not cut:
        cut = text[:max_chars].rstrip()
    return cut + "…"


def listing_excerpt(game: dict, *, words: int = 36, chars: int | None = None) -> str:
    """Prefer excerpt/summary/description, then what_is_it, then vibe."""
    source = ""
    for key in ("excerpt", "summary", "description"):
        source = _clean_text(game.get(key))
        if source:
            break
    if not source:
        source = _clean_text(game.get("what_is_it")) or _clean_text(game.get("vibe"))
    if not source:
        title = _clean_text(game.get("title")) or "This game"
        source = (
            f"{title} has an original J-Indie Radar dossier on its systems, "
            "its language barrier, and why Japanese players kept recommending it."
        )
    if chars:
        return _truncate_chars(source, chars)
    return _truncate_words(source, words)


def format_updated(value: str) -> str:
    raw = (value or "").strip()
    try:
        dt = datetime.strptime(raw[:10], "%Y-%m-%d")
    except ValueError:
        return raw
    return f"{dt.day} {dt.strftime('%b %Y')}"


def barrier_short(game: dict) -> str:
    raw = game.get("language_barrier")
    level = ""
    if isinstance(raw, dict):
        level = str(raw.get("level") or "")
    elif isinstance(raw, str):
        level = raw
    short = level.split("(", 1)[0].strip()
    return short or "Unrated"


def barrier_badge(game: dict) -> str:
    short = barrier_short(game)
    low = short.lower()
    if low.startswith("none"):
        return "No Japanese needed"
    if low.startswith("unrated"):
        return "Barrier unrated"
    return f"{short} barrier"


def prepare_listing(game: dict) -> dict:
    item = dict(game)
    item["excerpt"] = listing_excerpt(game, words=36)
    item["lead"] = listing_excerpt(game, chars=155)
    item["updated_label"] = format_updated(str(game.get("updated") or ""))
    item["barrier_label"] = barrier_badge(game)
    item["playtime_label"] = _clean_text(game.get("playtime_short")) or "Varies"
    return item


def pick_featured(games: list[dict], limit: int = 2) -> list[dict]:
    by_slug = {str(g.get("slug") or ""): g for g in games}
    picked: list[dict] = []
    seen: set[str] = set()

    def take(game: dict | None) -> None:
        if not game or len(picked) >= limit:
            return
        slug = str(game.get("slug") or "")
        if not slug or slug in seen:
            return
        seen.add(slug)
        picked.append(game)

    for game in games:
        if game.get("featured") is True:
            take(game)
    for slug in DEFAULT_FEATURED_SLUGS:
        take(by_slug.get(slug))
    newest = sorted(games, key=lambda g: str(g.get("updated") or ""), reverse=True)
    for game in newest:
        take(game)
    return picked


def _coerce_why(items) -> list[dict]:
    fixed: list[dict] = []
    if not isinstance(items, list):
        return fixed
    for item in items:
        if isinstance(item, dict):
            title = str(item.get("title") or "").strip()
            details = str(item.get("details") or "").strip()
            if title or details:
                fixed.append({"title": title or (details[:80] if details else "Note"), "details": details or title})
        elif isinstance(item, str) and item.strip():
            heading, _, rest = item.partition(".")
            fixed.append({"title": heading.strip() or item[:80], "details": (rest or item).strip()})
    return fixed


def _coerce_language_barrier(raw) -> dict:
    if isinstance(raw, dict):
        lb = dict(raw)
    elif isinstance(raw, str) and raw.strip():
        lb = {"level": raw.strip(), "details": raw.strip()}
    else:
        lb = {}
    level = str(lb.get("level") or "")
    low = level.lower()
    if low.startswith("none") or "visual" in low:
        level = "None (Visual/Action only)"
    elif low.startswith("low") or "basic ui" in low:
        level = "Low (Basic UI/Menu)"
    elif low.startswith("high") or "text-heavy" in low:
        level = "High (Text-Heavy/Lore)"
    elif low.startswith("medium") or "screen" in low:
        level = "Medium (Screen Translation OK)"
    elif not level:
        level = "Medium (Screen Translation OK)"
    lb["level"] = level
    lb.setdefault("details", level)
    if "score" not in lb:
        lb["score"] = 0 if level.startswith("None") else 1 if level.startswith("Low") else 2 if level.startswith("Medium") else 3
    return lb


def normalize_game(game: dict) -> dict:
    appid = int(game["appid"])
    out = dict(game)
    out["appid"] = appid
    if out.get("skip_steam") or out.get("steam_mismatch"):
        out.setdefault("header_image", "img/placeholder-header.svg")
        if out.get("steam_mismatch"):
            out["steam_url"] = out.get("store_url") or ""
        elif not out.get("steam_url"):
            out["steam_url"] = out.get("store_url") or ""
    else:
        urls = steam_urls(appid)
        out.setdefault("header_image", urls["header_image"])
        out.setdefault("steam_url", urls["steam_url"])
    out.setdefault("updated", date.today().isoformat())
    out.setdefault("genres", [out.get("primary_genre", "Action")])
    out["why_trending_in_japan"] = _coerce_why(out.get("why_trending_in_japan"))
    out["language_barrier"] = _coerce_language_barrier(out.get("language_barrier"))
    return out


def json_ld_website(cfg: dict) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": cfg["site_name"],
            "url": cfg["site_url"] + "/",
            "description": cfg["tagline"],
            "inLanguage": "en",
            "publisher": {"@type": "Organization", "name": cfg["site_name"], "url": cfg["site_url"] + "/"},
        },
        ensure_ascii=False,
    )


def json_ld_article(cfg: dict, game: dict) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{game['title']} — Japanese indie dossier",
            "description": f"{game['vibe']}. Language barrier: {game['language_barrier']['level']}.",
            "dateModified": game["updated"],
            "datePublished": f"{game['release_year']}-01-01",
            "inLanguage": "en",
            "author": {"@type": "Organization", "name": cfg["site_name"]},
            "publisher": {"@type": "Organization", "name": cfg["site_name"]},
            "image": absolute_media(cfg, game["header_image"]),
            "mainEntityOfPage": f"{cfg['site_url']}/games/{game['slug']}.html",
            "about": {"@type": "VideoGame", "name": game["title"], "author": game["developer"]},
        },
        ensure_ascii=False,
    )


def json_ld_about(cfg: dict, page_title: str, description: str, path: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page_title,
            "description": description,
            "url": cfg["site_url"] + path,
            "isPartOf": {"@type": "WebSite", "name": cfg["site_name"], "url": cfg["site_url"] + "/"},
        },
        ensure_ascii=False,
    )


def render_to(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="616" height="353" viewBox="0 0 616 353" role="img" aria-label="No store header">
  <rect width="616" height="353" fill="#141821"/>
  <rect x="24" y="24" width="568" height="305" fill="none" stroke="#f0c14b" stroke-opacity="0.35"/>
  <text x="308" y="170" text-anchor="middle" fill="#e8eaef" font-family="Segoe UI, sans-serif" font-size="28">J-Indie Radar</text>
  <text x="308" y="208" text-anchor="middle" fill="#9aa3b5" font-family="Segoe UI, sans-serif" font-size="16">No Steam header for this title</text>
</svg>
"""


def ensure_placeholder() -> None:
    dest = DOCS / "img" / "placeholder-header.svg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(PLACEHOLDER_SVG, encoding="utf-8")


def render_contact_body(raw: str, cfg: dict) -> str:
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    return env.from_string(raw).render(
        contact_email=cfg["contact_email"],
        google_form_embed=cfg["google_form_embed"],
    )


def write_robots_and_sitemap(cfg: dict, games: list[dict]) -> None:
    (DOCS / "robots.txt").write_text(
        "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                f"Sitemap: {cfg['site_url']}/sitemap.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )
    urls = [
        f"{cfg['site_url']}/index.html",
        f"{cfg['site_url']}/about.html",
        f"{cfg['site_url']}/privacy.html",
        f"{cfg['site_url']}/contact.html",
        f"{cfg['site_url']}/disclaimer.html",
        f"{cfg['site_url']}/sitemap.html",
    ]
    urls += [f"{cfg['site_url']}/games/{g['slug']}.html" for g in games]
    today = date.today().isoformat()
    parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{url}</loc>")
        parts.append(f"    <lastmod>{today}</lastmod>")
        parts.append("  </url>")
    parts.append("</urlset>")
    (DOCS / "sitemap.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def sitemap_page_body(games: list[dict]) -> str:
    from html import escape

    lines = [
        "<p>Every public page on J-Indie Radar is listed here: the editorial pages, and each Japanese indie dossier. The same URLs are also published for crawlers as <a href=\"sitemap.xml\">sitemap.xml</a>.</p>",
        "<h2>Site</h2>",
        "<ul>",
        '<li><a href="index.html">Home</a></li>',
        '<li><a href="about.html">About</a></li>',
        '<li><a href="privacy.html">Privacy Policy</a></li>',
        '<li><a href="contact.html">Contact</a></li>',
        '<li><a href="disclaimer.html">Disclaimer</a></li>',
        "</ul>",
        "<h2>Dossiers</h2>",
        "<ul>",
    ]
    for game in sorted(games, key=lambda g: str(g.get("title") or "").lower()):
        slug = escape(str(game.get("slug") or ""))
        title = escape(str(game.get("title") or "Untitled"))
        genre = escape(str(game.get("primary_genre") or ""))
        lines.append(f'<li><a href="games/{slug}.html">{title}</a> — {genre}</li>')
    lines.append("</ul>")
    return "\n".join(lines)


def build() -> list[dict]:
    cfg = site_config()
    env = jinja_env()
    ensure_placeholder()
    games = [normalize_game(g) for g in load_catalog()]
    games.sort(key=lambda g: (g.get("primary_genre", ""), g["title"]))
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "games.json").write_text(json.dumps(games, ensure_ascii=False, indent=2), encoding="utf-8")

    default_og = f"{cfg['site_url']}/img/placeholder-header.svg"
    if games:
        default_og = absolute_media(cfg, games[0]["header_image"])

    listings = [prepare_listing(g) for g in games]
    featured = pick_featured(listings, 2)
    index_html = env.get_template("index.html").render(
        page_title=f"{cfg['site_name']} — {cfg['tagline']}",
        meta_description="English dossiers on Japanese Steam indies: why they exploded in Japan, language-barrier grades, and systems analysis.",
        canonical=f"{cfg['site_url']}/index.html",
        og_type="website",
        og_image=default_og,
        json_ld=json_ld_website(cfg),
        root_prefix="",
        nav="home",
        games=listings,
        featured=featured,
        adsense_client_id=cfg["adsense_client_id"] if cfg["adsense_client_id"].startswith("ca-pub-") and "XXXX" not in cfg["adsense_client_id"] else "ca-pub-2075840815269276",
        ga_id=cfg["ga_id"] if cfg["ga_id"].startswith("G-") and "XXXX" not in cfg["ga_id"] else "",
        year=cfg["year"],
    )
    render_to(DOCS / "index.html", index_html)

    post_tmpl = env.get_template("post.html")
    games_dir = DOCS / "games"
    games_dir.mkdir(parents=True, exist_ok=True)
    adsense = "ca-pub-2075840815269276"
    ga = cfg["ga_id"] if cfg["ga_id"].startswith("G-") and "XXXX" not in cfg["ga_id"] else ""
    for game in games:
        html = post_tmpl.render(
            page_title=f"{game['title']} — J-Indie Radar",
            meta_description=f"{game['vibe']}. {game['language_barrier']['level']}. Independent English analysis of a Japanese indie.",
            canonical=f"{cfg['site_url']}/games/{game['slug']}.html",
            og_type="article",
            og_image=absolute_media(cfg, game["header_image"]),
            json_ld=json_ld_article(cfg, game),
            root_prefix="../",
            nav="home",
            game=game,
            adsense_client_id=adsense,
            ga_id=ga,
            year=cfg["year"],
        )
        render_to(games_dir / f"{game['slug']}.html", html)

    page_tmpl = env.get_template("page.html")
    for page in page_defs():
        body = page["body"]
        if page["slug"] == "contact":
            body = render_contact_body(body, cfg)
        html = page_tmpl.render(
            page_title=page["title"],
            meta_description=page["description"],
            canonical=f"{cfg['site_url']}/{page['slug']}.html",
            og_type="website",
            og_image=default_og,
            json_ld=json_ld_about(cfg, page["title"], page["description"], f"/{page['slug']}.html"),
            root_prefix="",
            nav=page["nav"],
            kicker=page["kicker"],
            heading=page["heading"],
            updated=date.today().isoformat(),
            body=body,
            adsense_client_id=adsense,
            ga_id=ga,
            year=cfg["year"],
        )
        render_to(DOCS / f"{page['slug']}.html", html)

    not_found = page_tmpl.render(
        page_title="Page not found — J-Indie Radar",
        meta_description="The requested dossier does not exist.",
        canonical=f"{cfg['site_url']}/404.html",
        og_type="website",
        og_image=default_og,
        json_ld=json_ld_website(cfg),
        root_prefix="",
        nav="home",
        kicker="404",
        heading="This signal faded",
        updated=date.today().isoformat(),
        body="<p>That URL is not on the radar. Return to the <a href='index.html'>catalog</a> or <a href='contact.html'>tell us</a> if a dossier should exist.</p>",
        adsense_client_id=adsense,
        ga_id=ga,
        year=cfg["year"],
    )
    render_to(DOCS / "404.html", not_found)
    sitemap_html = page_tmpl.render(
        page_title="Sitemap — J-Indie Radar",
        meta_description="HTML sitemap of J-Indie Radar: editorial pages and every Japanese indie dossier.",
        canonical=f"{cfg['site_url']}/sitemap.html",
        og_type="website",
        og_image=default_og,
        json_ld=json_ld_about(cfg, "Sitemap", "HTML sitemap of J-Indie Radar dossiers and editorial pages.", "/sitemap.html"),
        root_prefix="",
        nav="home",
        kicker="Index",
        heading="Sitemap",
        updated=date.today().isoformat(),
        body=sitemap_page_body(games),
        adsense_client_id=adsense,
        ga_id=ga,
        year=cfg["year"],
    )
    render_to(DOCS / "sitemap.html", sitemap_html)
    write_robots_and_sitemap(cfg, games)
    print(f"Built {len(games)} dossiers into {DOCS}")
    return games


if __name__ == "__main__":
    build()
