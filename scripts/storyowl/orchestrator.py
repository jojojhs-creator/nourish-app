"""Coffee, Cats & Malak — Tier 2 entrypoint: download an episode video and post it to YouTube.

TikTok is NOT handled here anymore — it is published natively via Higgsfield
(see docs/COFFEE_CATS_MALAK_RUNBOOK.md Step 5.5). This workflow only posts to YouTube.

Reads inputs from environment variables (set by the GitHub Actions workflow from either
a `repository_dispatch` payload or `workflow_dispatch` inputs), with optional CLI
overrides for local testing. YouTube is skipped (dry-run) if its credentials aren't
configured.
"""

import argparse
import json
import os
import sys

import downloader
import metadata
import youtube_uploader

OUT_DIR = "out"


def get_inputs() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-url")
    parser.add_argument("--thumbnail-url")
    parser.add_argument("--youtube-title")
    parser.add_argument("--youtube-description")
    parser.add_argument("--youtube-tags")
    parser.add_argument("--tiktok-caption")  # accepted but ignored (TikTok via Higgsfield)
    args = parser.parse_args()

    video_url = args.video_url or os.environ.get("VIDEO_URL", "")
    video_file = os.environ.get("VIDEO_FILE", "")  # local path — skips download
    if not video_url and not video_file:
        sys.exit("VIDEO_URL or VIDEO_FILE is required")

    tags_raw = args.youtube_tags or os.environ.get("YOUTUBE_TAGS", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    return {
        "video_url": video_url,
        "video_file": video_file,
        "thumbnail_url": args.thumbnail_url or os.environ.get("THUMBNAIL_URL", ""),
        "youtube_title": args.youtube_title or os.environ.get("YOUTUBE_TITLE", ""),
        "youtube_description": args.youtube_description or os.environ.get("YOUTUBE_DESCRIPTION", ""),
        "youtube_tags": tags,
    }


def write_outputs(inputs: dict, meta: dict, results: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "result.json"), "w", encoding="utf-8") as f:
        json.dump({"inputs": inputs, "metadata": meta, "results": results}, f, indent=2, ensure_ascii=False)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    lines = ["## Coffee, Cats & Malak — Auto-Post Results", "", "| Platform | Status | Details |", "|---|---|---|"]

    yt = results["youtube"]
    if yt["status"] == "uploaded":
        detail = yt["url"]
        if yt.get("thumbnail") == "uploaded":
            detail += " (custom thumbnail set)"
        elif yt.get("thumbnail") == "error":
            detail += f" (thumbnail not set: {yt.get('thumbnail_error', '')})"
        lines.append(f"| YouTube | uploaded | {detail} |")
    elif yt["status"] == "dry_run":
        lines.append("| YouTube | dry run (no credentials configured) | see generated metadata below |")
    else:
        lines.append(f"| YouTube | error | {yt.get('error', '')} |")

    lines.append("| TikTok | published separately via Higgsfield (not this workflow) | — |")

    lines += [
        "",
        "### Generated YouTube metadata",
        f"**Title:** {meta['youtube']['title']}",
        "",
        f"**Description:**\n```\n{meta['youtube']['description']}\n```",
        "",
        f"**Tags:** {', '.join(meta['youtube']['tags'])}",
    ]

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    inputs = get_inputs()

    video_path = inputs["video_file"] if inputs.get("video_file") else downloader.download_video(inputs["video_url"])

    thumbnail_path = None
    if inputs["thumbnail_url"]:
        try:
            thumbnail_path = downloader.download_thumbnail(inputs["thumbnail_url"])
        except Exception:  # noqa: BLE001 - thumbnail is optional, don't block posting
            thumbnail_path = None

    meta = {
        "youtube": metadata.ensure_youtube_metadata(
            inputs["youtube_title"], inputs["youtube_description"], inputs["youtube_tags"]
        ),
    }

    results: dict = {"youtube": None}
    had_error = False

    if youtube_uploader.is_configured():
        try:
            upload_result = youtube_uploader.upload_video(
                video_path,
                meta["youtube"]["title"],
                meta["youtube"]["description"],
                meta["youtube"]["tags"],
                thumbnail_path=thumbnail_path,
            )
            results["youtube"] = {"status": "uploaded", **upload_result}
        except Exception as exc:  # noqa: BLE001
            results["youtube"] = {"status": "error", "error": str(exc)}
            had_error = True
    else:
        results["youtube"] = {"status": "dry_run"}

    write_outputs(inputs, meta, results)

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
