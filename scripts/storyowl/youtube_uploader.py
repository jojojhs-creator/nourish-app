"""Upload a finished episode to YouTube as a public Short (general audience)."""

import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"
UPLOAD_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# "Entertainment" - change here if a different YouTube category fits better.
DEFAULT_CATEGORY_ID = "24"


def is_configured() -> bool:
    return bool(
        os.environ.get("YOUTUBE_CLIENT_ID")
        and os.environ.get("YOUTUBE_CLIENT_SECRET")
        and os.environ.get("YOUTUBE_REFRESH_TOKEN")
    )


def build_credentials() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri=TOKEN_URI,
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        scopes=UPLOAD_SCOPES,
    )


def set_thumbnail(youtube, video_id: str, thumbnail_path: str) -> None:
    media = MediaFileUpload(thumbnail_path, resumable=True)
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str | None = None,
    made_for_kids: bool = False,
) -> dict:
    credentials = build_credentials()
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": DEFAULT_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()

    video_id = response["id"]
    result = {"video_id": video_id, "url": f"https://youtube.com/shorts/{video_id}"}

    if thumbnail_path:
        try:
            set_thumbnail(youtube, video_id, thumbnail_path)
            result["thumbnail"] = "uploaded"
        except Exception as exc:  # noqa: BLE001 - thumbnail is best-effort, video upload already succeeded
            result["thumbnail"] = "error"
            result["thumbnail_error"] = str(exc)

    return result
