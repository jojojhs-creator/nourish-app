"""Download episode assets (video, thumbnail) to local files."""

import os

import requests


def _stream_download(url: str, dest_path: str, expected_content_types: tuple[str, ...]) -> str:
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if not any(t in content_type for t in expected_content_types):
            raise ValueError(
                f"Unexpected content-type '{content_type}' when downloading {url}"
            )

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return dest_path


def download_video(url: str, dest_dir: str = "/tmp", filename: str = "coffee_cats_malak.mp4") -> str:
    """Stream-download `url` to `dest_dir/filename` and return the local path."""
    if not url:
        raise ValueError("video_url is required")

    os.makedirs(dest_dir, exist_ok=True)
    return _stream_download(url, os.path.join(dest_dir, filename), ("video", "octet-stream"))


def download_thumbnail(url: str, dest_dir: str = "/tmp", filename: str | None = None) -> str:
    """Stream-download a thumbnail image `url` to `dest_dir/filename` and return the local path."""
    if not url:
        raise ValueError("thumbnail_url is required")

    if filename is None:
        # Keep the source extension so the upload mimetype matches the actual bytes.
        ext = os.path.splitext(url.split("?")[0])[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        filename = f"ccm_thumbnail{ext}"

    os.makedirs(dest_dir, exist_ok=True)
    return _stream_download(url, os.path.join(dest_dir, filename), ("image", "octet-stream"))
