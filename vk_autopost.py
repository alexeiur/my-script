#!/usr/bin/env python3
"""Simple script for auto posting to VK (vkontakte).

This script posts a message to a VK wall (user or group) using the VK API.
Provide an access token with permissions to post, the owner ID, and the
message you want to publish. Optionally specify attachments.

Usage example:

    python vk_autopost.py --token YOUR_TOKEN --owner-id -123456 --message "Hello"

The owner-id should be negative for groups and positive for user walls.
"""

from __future__ import annotations

import argparse
import os
from typing import Optional

import requests

API_URL = "https://api.vk.com/method/wall.post"
API_VERSION = "5.131"


def post_to_vk(access_token: str, owner_id: int, message: str, attachments: Optional[str] = None) -> dict:
    """Post a message to a VK wall using the API.

    Parameters
    ----------
    access_token: str
        VK API access token with the `wall` permission.
    owner_id: int
        ID of the user or community where the post will be published.
        For communities use negative ID.
    message: str
        Text of the post.
    attachments: Optional[str]
        Comma-separated list of attachments in VK format.

    Returns
    -------
    dict
        JSON response from the VK API.
    """

    payload = {
        "access_token": access_token,
        "owner_id": owner_id,
        "message": message,
        "v": API_VERSION,
    }
    if attachments:
        payload["attachments"] = attachments

    response = requests.post(API_URL, data=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        error = data["error"]
        raise RuntimeError(f"VK API error {error['error_code']}: {error['error_msg']}")

    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a message to VK wall")
    parser.add_argument("--token", default=os.getenv("VK_TOKEN"), help="VK access token (or VK_TOKEN env variable)")
    parser.add_argument("--owner-id", type=int, required=True, help="User ID or negative group ID to post on")
    parser.add_argument("--message", required=True, help="Text of the post")
    parser.add_argument("--attachments", help="Comma separated list of attachments", default=None)
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("Access token is required")

    result = post_to_vk(args.token, args.owner_id, args.message, args.attachments)
    post_id = result["response"]["post_id"]
    print(f"Posted successfully. post_id={post_id}")


if __name__ == "__main__":
    main()
