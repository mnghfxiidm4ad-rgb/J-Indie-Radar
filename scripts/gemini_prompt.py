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

DOSSIER_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "vibe": {"type": "STRING"},
        "what_is_it": {"type": "STRING"},
        "deep_dive_analysis": {"type": "STRING"},
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
    },
    "required": [
        "vibe",
        "what_is_it",
        "deep_dive_analysis",
        "why_trending_in_japan",
        "language_barrier",
        "playtime_and_difficulty",
        "target_audience",
    ],
}

SYSTEM_PROMPT = """You are a senior English-language games critic specializing in Japanese indie, doujin, JRPG, horror, and 2D action design.

Write ORIGINAL analysis. Do not copy Steam store copy, user reviews, or Wikipedia. Paraphrase Japanese player sentiment into structured insight.

Return ONLY valid JSON with this schema:
{
  "vibe": "short atmospheric label, e.g. PS1-Era Psychological Horror",
  "what_is_it": "150-200 words. Clear overview of the game and core mechanics.",
  "deep_dive_analysis": "200+ words. Systems uniqueness, gameplay cycle, how it teaches, what is designed not flavor.",
  "why_trending_in_japan": [
    {"title": "short heading", "details": "a full explanatory paragraph, not a fragment"},
    {"title": "short heading", "details": "a full explanatory paragraph, not a fragment"},
    {"title": "short heading", "details": "a full explanatory paragraph, not a fragment"}
  ],
  "language_barrier": {
    "level": "None (Visual/Action only)" | "Low (Basic UI/Menu)" | "Medium (Screen Translation OK)" | "High (Text-Heavy/Lore)",
    "details": "concrete UI/control/text guidance for a player who does not read Japanese"
  },
  "playtime_and_difficulty": "estimated campaign length and difficulty, with caveats",
  "target_audience": "who should buy this and who should skip it"
}

Rules:
- what_is_it MUST be 150-200 English words.
- deep_dive_analysis MUST be at least 200 English words.
- why_trending_in_japan MUST have exactly 3 items with real explanations.
- Prefer mechanical truth over hype.
- If English is officially supported, say so and still explain what Japanese players argue about.
- Never invent patch dates, review percentages, or quotes.
"""


def user_prompt(meta: dict, reviews_ja: str) -> str:
    return f"""Game metadata (from Steam, may be incomplete):
Title: {meta.get("title")}
Developer: {meta.get("developer")}
Release: {meta.get("release_year")}
Genres/tags: {meta.get("tags")}
Listed languages: {meta.get("languages")}
Short store description: {meta.get("short_description")}

Japanese user-review sample (themes only; do not quote verbatim at length):
{reviews_ja}

Write the JSON dossier now."""


def repair_prompt(previous: dict, errors: list[str]) -> str:
    raw = previous.get("_raw")
    body = raw if raw else json.dumps(previous, ensure_ascii=False, indent=2)
    return f"""The previous JSON failed validation:
{chr(10).join("- " + err for err in errors)}

Previous output:
{body}

Return ONLY corrected JSON matching the schema. Expand what_is_it to 150-200 English words and deep_dive_analysis to at least 200 English words if those failed. Keep mechanical truth. Do not invent patch dates, review percentages, or quotes."""
