#!/usr/bin/env python3
"""Simple script for auto posting to VK (vkontakte).

This script posts a message to one or multiple VK walls (user or group)
using the VK API. Provide access tokens with permissions to post, the owner
IDs, and the message you want to publish. Optionally specify attachments.

Usage examples:

Single wall:

    python vk_autopost.py --token YOUR_TOKEN --owner-id -123456 --message "Hello"

Two different walls (two accounts):

    python vk_autopost.py --account TOKEN1:-123 --account TOKEN2:456 --message "Hello"

Nine groups with a single token:

    python vk_autopost.py --token YOUR_TOKEN \
        --group -1 --group -2 --group -3 --group -4 --group -5 \
        --group -6 --group -7 --group -8 --group -9 \
        --message "Hello"

Owner IDs should be negative for groups and positive for user walls.
"""

from __future__ import annotations

import argparse
import os
from typing import List, Optional, Tuple

import requests

API_URL = "https://api.vk.com/method/wall.post"
API_VERSION = "5.131"


def parse_account(pair: str) -> Tuple[str, int]:
    """Parse account definition in format TOKEN:OWNER_ID."""
    token, owner = pair.split(":", 1)
    return token, int(owner)


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
    parser.add_argument(
        "--token",
        default=os.getenv("VK_TOKEN"),
        help="VK access token (or VK_TOKEN env variable) for single posting",
    )
    parser.add_argument("--owner-id", type=int, help="User ID or negative group ID to post on")
    parser.add_argument(
        "--group",
        dest="groups",
        action="append",
        type=int,
        help="Negative group ID to post on; can be passed multiple times",
        default=[],
    )
    parser.add_argument(
        "--account",
        action="append",
        metavar="TOKEN:OWNER_ID",
        help="Post using token:owner_id pair; can be passed multiple times",
        default=[],
    )
    parser.add_argument("--message", required=True, help="Text of the post")
    parser.add_argument("--attachments", help="Comma separated list of attachments", default=None)
    args = parser.parse_args()

    accounts: List[Tuple[str, int]] = []
    if args.account:
        accounts = [parse_account(a) for a in args.account]
    elif args.groups:
        if not args.token:
            raise SystemExit("Access token is required")
        accounts = [(args.token, g) for g in args.groups]
    else:
        if not args.token:
            raise SystemExit("Access token is required")
        if args.owner_id is None:
            raise SystemExit("--owner-id required when --account or --group not used")
        accounts = [(args.token, args.owner_id)]

    for token, owner_id in accounts:
        result = post_to_vk(token, owner_id, args.message, args.attachments)
        post_id = result["response"]["post_id"]
        print(f"Posted for owner_id={owner_id}. post_id={post_id}")


if __name__ == "__main__":
    main()
