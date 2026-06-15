"""Upload a finished episode to TikTok via the Content Posting API.

`post_mode` controls which endpoint/privacy level is used, so the pipeline can
"graduate" from unaudited drafts to fully public posting purely via the
TIKTOK_POST_MODE repo variable - no code changes needed.

  DRAFT             -> /v2/post/publish/inbox/video/init/ (creator's inbox, no audit
                       needed; the user finishes posting from the TikTok app)
  SELF_ONLY         -> /v2/post/publish/video/init/ with privacy_level=SELF_ONLY
                       (private Direct Post, available pre-audit)
  PUBLIC_TO_EVERYONE -> /v2/post/publish/video/init/ with privacy_level=PUBLIC_TO_EVERYONE
                       (requires approved Content Posting API access)
"""

import os
import time

import requests

API_BASE = "https://open.tiktokapis.com"
TOKEN_URL = f"{API_BASE}/v2/oauth/token/"
INBOX_INIT_URL = f"{API_BASE}/v2/post/publish/inbox/video/init/"
DIRECT_INIT_URL = f"{API_BASE}/v2/post/publish/video/init/"
STATUS_URL = f"{API_BASE}/v2/post/publish/status/fetch/"

DEFAULT_POST_MODE = "DRAFT"
VALID_POST_MODES = {"DRAFT", "SELF_ONLY", "PUBLIC_TO_EVERYONE"}

STATUS_POLL_INTERVAL_SECONDS = 5
STATUS_POLL_MAX_ATTEMPTS = 24  # ~2 minutes


def is_configured() -> bool:
    return bool(
        os.environ.get("TIKTOK_CLIENT_KEY")
        and os.environ.get("TIKTOK_CLIENT_SECRET")
        and os.environ.get("TIKTOK_REFRESH_TOKEN")
    )


def refresh_access_token() -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_key": os.environ["TIKTOK_CLIENT_KEY"],
            "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise RuntimeError(f"TikTok token refresh failed: {data}")
    return data["access_token"]


def _init_upload(access_token: str, video_size: int, caption: str, post_mode: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    source_info = {
        "source": "FILE_UPLOAD",
        "video_size": video_size,
        "chunk_size": video_size,
        "total_chunk_count": 1,
    }

    if post_mode == "DRAFT":
        body = {"source_info": source_info}
        url = INBOX_INIT_URL
    else:
        body = {
            "post_info": {
                "title": caption,
                "privacy_level": post_mode,
                "disable_duplicate_check": True,
            },
            "source_info": source_info,
        }
        url = DIRECT_INIT_URL

    response = requests.post(url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    if data.get("error", {}).get("code") not in (None, "ok"):
        raise RuntimeError(f"TikTok init failed: {data}")
    return data["data"]


def _upload_video_bytes(upload_url: str, video_path: str, video_size: int) -> None:
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
    }
    response = requests.put(upload_url, data=video_bytes, headers=headers, timeout=300)
    response.raise_for_status()


def _poll_status(access_token: str, publish_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    for _ in range(STATUS_POLL_MAX_ATTEMPTS):
        response = requests.post(
            STATUS_URL, json={"publish_id": publish_id}, headers=headers, timeout=30
        )
        response.raise_for_status()
        status = response.json().get("data", {}).get("status")
        if status in ("PUBLISH_COMPLETE", "FAILED"):
            return status
        time.sleep(STATUS_POLL_INTERVAL_SECONDS)
    return "TIMEOUT"


def upload_video(video_path: str, caption: str, post_mode: str) -> dict:
    post_mode = (post_mode or DEFAULT_POST_MODE).strip().upper()
    if post_mode not in VALID_POST_MODES:
        post_mode = DEFAULT_POST_MODE

    access_token = refresh_access_token()
    video_size = os.path.getsize(video_path)

    init_data = _init_upload(access_token, video_size, caption, post_mode)
    upload_url = init_data["upload_url"]
    publish_id = init_data.get("publish_id")

    _upload_video_bytes(upload_url, video_path, video_size)

    if post_mode == "DRAFT":
        return {"publish_id": publish_id, "status": "SENT_TO_INBOX", "mode": post_mode}

    status = _poll_status(access_token, publish_id)
    return {"publish_id": publish_id, "status": status, "mode": post_mode}
