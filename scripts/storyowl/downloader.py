"""Download the finished episode video to a local file."""

import os

import requests


def download_video(url: str, dest_dir: str = "/tmp", filename: str = "storyowl_video.mp4") -> str:
    """Stream-download `url` to `dest_dir/filename` and return the local path."""
    if not url:
        raise ValueError("video_url is required")

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "video" not in content_type and "octet-stream" not in content_type:
            raise ValueError(
                f"Unexpected content-type '{content_type}' when downloading {url}"
            )

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return dest_path
