"""Gemini prompt used to generate AdSense-ready English dossiers."""

import json

# gemini-1.5-flash was shut down in 2025. Prefer current Flash aliases.
GEMINI_MODEL_DEFAULT = "gemini-3.5-flash"
GEMINI_MODEL_FALLBACKS = (
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash",
)

LANGUAGE_LEVELS = (
    "None (Visual/Action only)",
    "Low (Basic UI/Menu)",
    "Medium (Screen Translation OK)",
    "High (Text-Heavy/Lore)",
)

FACT_UNKNOWN = "Not provided in Steam data"

DOSSIER_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "headline": {"type": "STRING"},
        "vibe": {"type": "STRING"},
        "what_is_it": {"type": "STRING"},
        "deep_dive_analysis": {"type": "STRING"},
        "visuals_audio_identity": {"type": "STRING"},
        "why_trending_in_japan": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "details": {"type": "STRING"},
                },
                "required": ["title", "details"],
            },
        },
        "community_quote": {"type": "STRING"},
        "language_barrier": {
            "type": "OBJECT",
            "properties": {
                "level": {"type": "STRING", "enum": list(LANGUAGE_LEVELS)},
                "details": {"type": "STRING"},
            },
            "required": ["level", "details"],
        },
        "playtime_and_difficulty": {"type": "STRING"},
        "target_audience": {"type": "STRING"},
        "radar_score": {"type": "STRING"},
    },
    "required": [
        "headline",
        "vibe",
        "what_is_it",
        "deep_dive_analysis",
        "visuals_audio_identity",
        "why_trending_in_japan",
        "community_quote",
        "language_barrier",
        "playtime_and_difficulty",
        "target_audience",
        "radar_score",
    ],
}

SYSTEM_PROMPT = """You are a senior video game design analyst and Japanese indie curator writing for "J-Indie Radar" — an exclusive English publication uncovering overlooked gems, experimental doujin titles, and unique mechanical designs on Steam from Japan.

### Editorial Tone & Guidelines:
1. Systems & Mechanics First: Avoid superficial store page summaries. Analyze the gameplay loops, core friction, input feel, and mechanical synergy that define the title.
2. Aesthetic & Narrative Subtext: Critique visual direction, soundscape integration, and thematic subtleties (e.g., pixel art craftsmanship, ambient audio, environmental storytelling).
3. Japanese Indie Context: Provide cultural context on how the title fits into Japan's independent development scene (doujin lineage, solo-dev philosophy, or distinct genre interpretations).
4. Tone of Voice: Intelligent, analytical, enthusiastic about indie craftsmanship, and culturally observant (comparable to Rock Paper Shotgun, Edge Magazine, or deep-dive game design video essays). Avoid clickbait tropes or hyperbolic empty praise.
5. Formatting: Write each JSON string field as clean, highly readable English. Use short bullet lists inside a field only when they clarify a system. Do not repeat H1/H2 headings inside the fields — the site template supplies those. Use a single blockquote-ready line for the Japanese player impression.
6. Language: Natural, sophisticated English geared toward discerning gamers and indie enthusiasts.

### Output contract
Return ONLY valid JSON matching the schema. Map the editorial article onto these keys:

{
  "headline": "catchy subtitle highlighting the core hook or design philosophy (do not repeat the game title)",
  "vibe": "short atmospheric catalog label, e.g. PS1-Era Psychological Horror",
  "what_is_it": "Section 1 — The Hook & Core Philosophy. 150-220 words. Immediate breakdown of what makes this game mechanically or atmospherically unique.",
  "deep_dive_analysis": "Section 2 — Mechanical Architecture & Game Loop. 200+ words. Controls, pacing, feedback loop, system depth, and mechanical synergy.",
  "visuals_audio_identity": "Section 3 — Visuals, Audio & Atmospheric Identity. 120+ words. Art style, color palettes, sound design, and immersion.",
  "why_trending_in_japan": [
    {"title": "short heading", "details": "a full paragraph synthesizing domestic player feedback, difficulty perception, or cult acclaim"},
    {"title": "short heading", "details": "a full explanatory paragraph"},
    {"title": "short heading", "details": "a full explanatory paragraph"}
  ],
  "community_quote": "one short English translation of a typical Japanese player impression, suitable as a blockquote. Never invent a named reviewer. If Japanese reviews are missing, say that consensus is too thin to quote faithfully.",
  "language_barrier": {
    "level": "None (Visual/Action only)" | "Low (Basic UI/Menu)" | "Medium (Screen Translation OK)" | "High (Text-Heavy/Lore)",
    "details": "concrete UI/control/text guidance for a player who does not read Japanese, using only the verified language list"
  },
  "playtime_and_difficulty": "estimated campaign length and difficulty, with caveats; do not invent exact hours if the verified data does not support a confident estimate — hedge instead",
  "target_audience": "Section 5 — Radar Verdict & Steam Accessibility. Who this game is for, language-barrier notes if applicable, and who should skip it.",
  "radar_score": "final recommendation score/quote, e.g. 8/10 — a compact authored pull-quote, not a fake Metacritic number"
}

### Factual accuracy (non-negotiable)
- Only reference the developer, publisher, release date, review status, tags/genres, language options, and store URL supplied in [VERIFIED STEAM METADATA].
- NEVER invent, assume, or hallucinate store facts, pricing, discounts, player counts, patch dates, or system specifications.
- If specific historical lore of the creator is not provided, analyze the design craft of the game itself rather than making up developer backstories.
- Do not copy Steam store copy, user reviews, or Wikipedia. Paraphrase Japanese player sentiment into structured insight.
- Never invent review percentages or quotes that are not grounded in the verified metadata or the Japanese review sample.
"""


def _meta_text(meta: dict, *keys: str) -> str:
    for key in keys:
        value = meta.get(key)
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            text = ", ".join(str(item).strip() for item in value if str(item).strip())
        else:
            text = str(value).strip()
        if text:
            return text
    return FACT_UNKNOWN


def verified_metadata_block(meta: dict) -> str:
    """Ground the model on Steam-fetched facts so it cannot invent store data."""
    return f"""---
[VERIFIED STEAM METADATA]
- Title: {_meta_text(meta, "title", "game_title")}
- Developer / Publisher: {_meta_text(meta, "developer", "developer_name")} / {_meta_text(meta, "publisher", "publisher_name")}
- Release Date: {_meta_text(meta, "release_date", "release_year")}
- Steam Review Status: {_meta_text(meta, "review_summary", "review_status")}
- Tags / Genres: {_meta_text(meta, "tags", "tags_list", "genres")}
- Supported Languages: {_meta_text(meta, "languages", "languages_list")}
- Store URL: {_meta_text(meta, "store_url", "steam_url")}
- Price: NOT IN VERIFIED DATA (do not mention a specific price or discount)
- System specifications: NOT IN VERIFIED DATA (do not invent hardware requirements)

CRITICAL RULES FOR FACTUAL ACCURACY:
- Only reference the developer, publisher, release date, and language options provided above.
- NEVER invent, assume, or hallucinate store facts, pricing, or system specifications.
- If specific historical lore of the creator is not provided, analyze the design craft of the game itself rather than making up developer backstories.
---"""


def article_template_block(meta: dict) -> str:
    title = _meta_text(meta, "title", "game_title")
    return f"""Write the dossier as this article, then encode it into the JSON keys (do not wrap the response in Markdown fences):

H1: {title} Deep Dive: [Catchy Subtitle highlighting the core hook or design philosophy]
  → JSON "headline" is the subtitle only.

1. The Hook & Core Philosophy (Immediate breakdown of what makes this game mechanically or atmospherically unique)
  → JSON "what_is_it" and a short catalog "vibe".

2. Mechanical Architecture & Game Loop (In-depth analysis of controls, pacing, feedback loop, and system depth)
  → JSON "deep_dive_analysis".

3. Visuals, Audio & Atmospheric Identity (Evaluation of art style, color palettes, sound design, and immersion)
  → JSON "visuals_audio_identity".

4. Community Reception & Japanese Player Consensus (Synthesis of domestic player feedback, difficulty perception, and cult acclaim with a translated quote)
  → JSON "why_trending_in_japan" (exactly 3 items) and "community_quote".

5. Radar Verdict & Steam Accessibility (Who this game is for, language barrier notes if applicable, and final recommendation score/quote)
  → JSON "target_audience", "language_barrier", "playtime_and_difficulty", and "radar_score"."""


def user_prompt(meta: dict, reviews_ja: str) -> str:
    store_blurb = _meta_text(meta, "short_description")
    blurb_line = (
        f"Store blurb (context only — do not rewrite this as the article):\n{store_blurb}"
        if store_blurb != FACT_UNKNOWN
        else "Store blurb: Not provided in Steam data."
    )
    return f"""{verified_metadata_block(meta)}

{blurb_line}

Japanese user-review sample (themes only; translate/synthesize, do not quote verbatim at length, never invent a named reviewer):
{reviews_ja}

{article_template_block(meta)}

Write the JSON dossier now."""


def repair_prompt(previous: dict, errors: list[str]) -> str:
    raw = previous.get("_raw")
    body = raw if raw else json.dumps(previous, ensure_ascii=False, indent=2)
    return f"""The previous JSON failed validation:
{chr(10).join("- " + err for err in errors)}

Previous output:
{body}

Return ONLY corrected JSON matching the schema.
- headline: catchy subtitle, not the full H1
- what_is_it: 150-220 English words (Hook & Core Philosophy)
- deep_dive_analysis: at least 200 English words (Mechanical Architecture & Game Loop)
- visuals_audio_identity: at least 120 English words
- why_trending_in_japan: exactly 3 items with title and details
- community_quote, radar_score, language_barrier, playtime_and_difficulty, target_audience must be present
Keep mechanical truth. Reuse only facts from the verified Steam metadata. Do not invent patch dates, prices, system specs, review percentages, or quotes."""
