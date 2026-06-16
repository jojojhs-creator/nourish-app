"""One-time helper: mint a long-lived YouTube upload refresh token.

Run this LOCALLY (not in CI). Unlike n8n's "Sign in with Google" (which needs a desktop
browser popup), this uses a copy/paste redirect flow that works from any device:

  1. The script prints an authorization URL.
  2. Open that URL in ANY browser (phone, laptop, doesn't matter) and approve access.
  3. The browser will redirect to http://localhost/?code=... and fail to load - that's
     expected. Copy the FULL URL from the address bar.
  4. Paste it back into this script's prompt.

Prerequisites:
  - A Google Cloud project with the "YouTube Data API v3" enabled.
  - An OAuth client ID of type "Desktop app" (Console > APIs & Services > Credentials).
  - The OAuth consent screen set to "Production" (not "Testing"), otherwise the
    refresh token this script prints will expire after 7 days.

Usage:
  pip install -r scripts/storyowl/local_auth/requirements-local.txt
  python scripts/storyowl/local_auth/youtube_oauth.py --client-secrets path/to/client_secret.json
"""

import argparse

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--client-secrets",
        required=True,
        help="Path to the OAuth client JSON downloaded from Google Cloud Console (Desktop app type)",
    )
    args = parser.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secrets, scopes=SCOPES)
    flow.redirect_uri = "http://localhost"

    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")

    print("\n1. Open this URL in any browser and approve access:\n")
    print(auth_url)
    print("\n2. After approving, the browser will redirect to a localhost URL that")
    print("   fails to load - that's expected. Copy the FULL URL from the address bar.")

    redirect_response = input("\n3. Paste the full redirect URL here: ").strip()

    flow.fetch_token(authorization_response=redirect_response)
    credentials = flow.credentials

    print("\nSuccess! Add these as GitHub repo secrets:\n")
    print(f"YOUTUBE_CLIENT_ID={credentials.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={credentials.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print(
        "\nReminder: the OAuth consent screen must be in 'Production' publishing "
        "status, or this refresh token will stop working after 7 days."
    )


if __name__ == "__main__":
    main()
