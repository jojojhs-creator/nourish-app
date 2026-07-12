"""StoryOwl Tier 2 entrypoint: download an episode video and post it to YouTube + TikTok.

Reads inputs from environment variables (set by the GitHub Actions workflow from either
a `repository_dispatch` payload or `workflow_dispatch` inputs), with optional CLI
overrides for local testing.

Each platform is skipped (dry-run) if its credentials aren't configured - this lets the
pipeline be exercised end-to-end (download + metadata generation) before OAuth setup is
complete.
"""

import argparse
import json
import os
import sys

import downloader
import metadata
import tiktok_uploader
import youtube_uploader

OUT_DIR = "out"


def get_inputs() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-url")
    parser.add_argument("--thumbnail-url")
    parser.add_argument("--youtube-title")
    parser.add_argument("--youtube-description")
    parser.add_argument("--youtube-tags")
    parser.add_argument("--tiktok-caption")
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
        "tiktok_caption": args.tiktok_caption or os.environ.get("TIKTOK_CAPTION", ""),
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

    tt = results["tiktok"]
    if tt["status"] == "uploaded":
        lines.append(f"| TikTok | uploaded ({tt['mode']}) | publish_id={tt['publish_id']}, status={tt['status_detail']} |")
    elif tt["status"] == "dry_run":
        lines.append(f"| TikTok | dry run (mode={tt['post_mode']}) | see generated caption below |")
    else:
        lines.append(f"| TikTok | error | {tt.get('error', '')} |")

    lines += [
        "",
        "### Generated YouTube metadata",
        f"**Title:** {meta['youtube']['title']}",
        "",
        f"**Description:**\n```\n{meta['youtube']['description']}\n```",
        "",
        f"**Tags:** {', '.join(meta['youtube']['tags'])}",
        "",
        "### Generated TikTok caption",
        f"```\n{meta['tiktok']['caption']}\n```",
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
        "tiktok": {"caption": metadata.ensure_tiktok_caption(inputs["tiktok_caption"], inputs["youtube_title"])},
    }

    results: dict = {"youtube": None, "tiktok": None}
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
        except Exception as exc:  # noqa: BLE001 - report and continue with TikTok
            results["youtube"] = {"status": "error", "error": str(exc)}
            had_error = True
    else:
        results["youtube"] = {"status": "dry_run"}

    post_mode = os.environ.get("TIKTOK_POST_MODE", tiktok_uploader.DEFAULT_POST_MODE)
    if tiktok_uploader.is_configured():
        try:
            upload_result = tiktok_uploader.upload_video(video_path, meta["tiktok"]["caption"], post_mode)
            results["tiktok"] = {
                "status": "uploaded",
                "mode": upload_result["mode"],
                "publish_id": upload_result["publish_id"],
                "status_detail": upload_result["status"],
            }
        except Exception as exc:  # noqa: BLE001
            results["tiktok"] = {"status": "error", "error": str(exc)}
            had_error = True
    else:
        results["tiktok"] = {"status": "dry_run", "post_mode": post_mode}

    write_outputs(inputs, meta, results)

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
