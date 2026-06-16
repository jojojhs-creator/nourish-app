"""One-time helper: mint a TikTok Content Posting API refresh token.

Run this LOCALLY (not in CI). Works from any device via copy/paste - no popup needed.

Prerequisites:
  - A TikTok Developer app at https://developers.tiktok.com with the "Content Posting
    API" product added.
  - A redirect URI registered on the app (any value works, e.g. https://localhost/callback
    - it doesn't need to resolve, you'll just copy the code from the failed redirect).

Usage:
  python scripts/storyowl/local_auth/tiktok_oauth.py \
      --client-key YOUR_CLIENT_KEY \
      --client-secret YOUR_CLIENT_SECRET \
      --redirect-uri https://localhost/callback

Steps:
  1. The script prints an authorization URL.
  2. Open it in any browser and approve access.
  3. You'll be redirected to your redirect URI with ?code=...&state=... in the address
     bar (the page itself may fail to load - that's fine). Copy the FULL URL.
  4. Paste it back into this script's prompt.
"""

import argparse
import secrets
import urllib.parse

import requests

AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
SCOPES = "video.upload,video.publish"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-key", required=True)
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--redirect-uri", required=True)
    args = parser.parse_args()

    state = secrets.token_urlsafe(16)
    params = {
        "client_key": args.client_key,
        "scope": SCOPES,
        "response_type": "code",
        "redirect_uri": args.redirect_uri,
        "state": state,
    }
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    print("\n1. Open this URL in any browser and approve access:\n")
    print(auth_url)
    print("\n2. After approving, you'll be redirected to your redirect URI with")
    print("   ?code=...&state=... in the address bar (the page may fail to load -")
    print("   that's fine). Copy the FULL URL.")

    redirect_response = input("\n3. Paste the full redirect URL here: ").strip()
    parsed = urllib.parse.urlparse(redirect_response)
    query = urllib.parse.parse_qs(parsed.query)

    if query.get("state", [None])[0] != state:
        raise SystemExit("State mismatch - please re-run and use the freshly printed URL.")

    code = query.get("code", [None])[0]
    if not code:
        raise SystemExit("No 'code' parameter found in the pasted URL.")

    response = requests.post(
        TOKEN_URL,
        data={
            "client_key": args.client_key,
            "client_secret": args.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": args.redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if "refresh_token" not in data:
        raise SystemExit(f"Token exchange failed: {data}")

    print("\nSuccess! Add these as GitHub repo secrets/variables:\n")
    print(f"TIKTOK_CLIENT_KEY={args.client_key}")
    print(f"TIKTOK_CLIENT_SECRET={args.client_secret}")
    print(f"TIKTOK_REFRESH_TOKEN={data['refresh_token']}")
    print(
        "\nStart with the TIKTOK_POST_MODE repo variable set to DRAFT until your "
        "Content Posting API access is approved for Direct Post (SELF_ONLY / "
        "PUBLIC_TO_EVERYONE)."
    )


if __name__ == "__main__":
    main()
