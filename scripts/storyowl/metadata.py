"""Fallback/enrichment for StoryOwl episode metadata.

The generation runbook (Tier 1) normally writes the real YouTube title/description/tags
and TikTok caption for each episode. These helpers only fill in gaps so the Tier 2
pipeline still produces something reasonable if a field is missing (e.g. a manual
workflow_dispatch run with partial inputs).
"""

import re

CURATED_HASHTAGS = [
    "#CoffeeCatsMalak",
    "#Cats",
    "#FunnyCats",
    "#CatsOfTikTok",
    "#CatLife",
    "#CatAnimation",
    "#CuteCats",
    "#Cozy",
    "#Shorts",
    "#fyp",
]

STOPWORDS = {
    "the", "a", "an", "and", "of", "to", "in", "with", "for", "on", "at",
    "by", "is", "are", "was", "were", "this", "that", "from", "as", "it",
}

YOUTUBE_TITLE_MAX = 100
YOUTUBE_DESCRIPTION_MAX = 5000
YOUTUBE_TAGS_CHAR_BUDGET = 460  # leave headroom under the 500-char API limit
YOUTUBE_TAG_MAX = 100

TIKTOK_CAPTION_MAX = 2200


def extract_keywords(title: str, max_keywords: int = 4) -> list[str]:
    """Derive simple hashtag-style keywords from an episode title."""
    if not title:
        return []

    words = re.findall(r"[A-Za-z؀-ۿ]+", title)
    significant = [w for w in words if w.lower() not in STOPWORDS and len(w) > 1]

    keywords = []
    if significant:
        combined = "".join(w.capitalize() for w in significant)
        if combined:
            keywords.append(f"#{combined}")

    for word in significant[:max_keywords]:
        tag = f"#{word.capitalize()}"
        if tag not in keywords:
            keywords.append(tag)

    return keywords[:max_keywords]


def ensure_youtube_metadata(title: str, description: str, tags: list[str]) -> dict:
    """Fill in any missing YouTube title/description/tags."""
    title = (title or "Coffee, Cats & Malak").strip()
    if len(title) > YOUTUBE_TITLE_MAX:
        title = title[: YOUTUBE_TITLE_MAX - 1].rstrip() + "…"

    description = (description or "").strip()
    if not description:
        description = f"{title}\n\nOne girl, three cats, zero peace and quiet ☕😹 New episode every day."

    if "#shorts" not in description.lower():
        description = f"{description}\n\n#Shorts"

    if len(description) > YOUTUBE_DESCRIPTION_MAX:
        description = description[: YOUTUBE_DESCRIPTION_MAX - 1].rstrip() + "…"

    merged: list[str] = []
    for tag in (tags or []) + [h.lstrip("#") for h in CURATED_HASHTAGS] + [
        h.lstrip("#") for h in extract_keywords(title)
    ]:
        tag = tag.strip()
        if not tag or len(tag) > YOUTUBE_TAG_MAX:
            continue
        if tag.lower() not in {t.lower() for t in merged}:
            merged.append(tag)

    budgeted: list[str] = []
    used = 0
    for tag in merged:
        # +1 accounts for the comma joining tags in the API request
        cost = len(tag) + (1 if budgeted else 0)
        if used + cost > YOUTUBE_TAGS_CHAR_BUDGET:
            break
        budgeted.append(tag)
        used += cost

    return {"title": title, "description": description, "tags": budgeted}


def ensure_tiktok_caption(caption: str, title: str) -> str:
    """Fill in (or top up) the TikTok caption with hashtags."""
    caption = (caption or "").strip()

    if not caption:
        caption = (title or "Coffee, Cats & Malak").strip()

    hashtags = [h for h in CURATED_HASHTAGS + extract_keywords(title) if h.lower() not in caption.lower()]

    result = caption
    for tag in hashtags:
        candidate = f"{result} {tag}"
        if len(candidate) > TIKTOK_CAPTION_MAX:
            break
        result = candidate

    if len(result) > TIKTOK_CAPTION_MAX:
        truncated = result[:TIKTOK_CAPTION_MAX]
        last_space = truncated.rfind(" ")
        result = truncated[:last_space] if last_space > 0 else truncated

    return result
