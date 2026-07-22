#!/usr/bin/env python3
"""Upload README demo video to GitHub's user-attachments CDN.

GitHub READMEs only render inline <video> players for files hosted on
github.com/user-attachments/assets/ (or user-images.githubusercontent.com).
Repo-local MP4 paths are stripped by GitHub's markdown sanitizer.

Usage:
  export GITHUB_USER_SESSION="<your github.com user_session cookie>"
  python scripts/upload_readme_demo_video.py

Optional:
  --video docs/assets/prediction.mp4
  --owner lwan1 --repo movienet-scene-segmentation
  --update-readme
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = REPO_ROOT / "docs" / "assets" / "prediction.mp4"
README_PATH = REPO_ROOT / "README.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--owner", default="lwan1")
    parser.add_argument("--repo", default="movienet-scene-segmentation")
    parser.add_argument(
        "--session",
        default=os.environ.get("GITHUB_USER_SESSION", ""),
        help="github.com user_session cookie (or set GITHUB_USER_SESSION)",
    )
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Replace README demo embed with the uploaded asset URL",
    )
    return parser.parse_args()


def repo_id(session: requests.Session, owner: str, repo: str) -> int:
    response = session.get(f"https://api.github.com/repos/{owner}/{repo}")
    response.raise_for_status()
    return response.json()["id"]


def upload_token(session: requests.Session, owner: str, repo: str) -> str:
    response = session.get(f"https://github.com/{owner}/{repo}")
    response.raise_for_status()
    match = re.search(r'"uploadToken":"([^"]+)"', response.text)
    if not match:
        raise RuntimeError("Could not find uploadToken; is user_session valid?")
    return match.group(1)


def upload_video(
    session: requests.Session,
    *,
    owner: str,
    repo: str,
    video_path: Path,
) -> str:
    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    size = video_path.stat().st_size
    if size > 10 * 1024 * 1024:
        raise ValueError(f"Video is {size / 1024 / 1024:.1f} MB; GitHub free-plan limit is 10 MB")

    repository_id = repo_id(session, owner, repo)
    token = upload_token(session, owner, repo)

    policy_response = session.post(
        "https://github.com/upload/policies/assets",
        headers={
            "accept": "application/json",
            "origin": "https://github.com",
            "referer": f"https://github.com/{owner}/{repo}",
            "x-requested-with": "XMLHttpRequest",
        },
        files={
            "name": (None, video_path.name),
            "size": (None, str(size)),
            "content_type": (None, "video/mp4"),
            "authenticity_token": (None, token),
            "repository_id": (None, str(repository_id)),
        },
        timeout=60,
    )
    if policy_response.status_code != 201:
        raise RuntimeError(
            f"Upload policy failed ({policy_response.status_code}): {policy_response.text[:500]}"
        )

    policy = policy_response.json()
    form = policy["form"]
    s3_fields = [(key, (None, str(value))) for key, value in form.items()]
    with video_path.open("rb") as handle:
        s3_response = session.post(
            policy["upload_url"],
            files=[*s3_fields, ("file", (video_path.name, handle, "video/mp4"))],
            timeout=120,
        )
    if s3_response.status_code not in (200, 204):
        raise RuntimeError(
            f"S3 upload failed ({s3_response.status_code}): {s3_response.text[:500]}"
        )

    finalize_response = session.put(
        f"https://github.com{policy['asset_upload_url']}",
        headers={
            "accept": "application/json",
            "origin": "https://github.com",
            "referer": f"https://github.com/{owner}/{repo}",
            "x-requested-with": "XMLHttpRequest",
        },
        files={
            "authenticity_token": (None, policy["asset_upload_authenticity_token"]),
        },
        timeout=60,
    )
    if finalize_response.status_code != 200:
        raise RuntimeError(
            f"Finalize failed ({finalize_response.status_code}): {finalize_response.text[:500]}"
        )

    return finalize_response.json()["href"]


def patch_readme(asset_url: str) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    block = (
        "## Demo\n\n"
        "Sample **predicted scene boundaries** from the BaSSL-inspired pipeline on a MovieNet-318 clip. "
        "Each segment shows keyframes grouped by the model’s predicted scene cuts "
        "(see the visualization cells in [`test_scene_seg_bassl.ipynb`](notebooks/test_scene_seg_bassl.ipynb)):\n\n"
        f'<video src="{asset_url}" controls playsinline width="100%"></video>\n'
    )
    if "## Demo" not in text:
        raise RuntimeError("README.md is missing a ## Demo section")
    text = re.sub(r"## Demo\n.*?(?=\n## Quick start\n)", block, text, count=1, flags=re.S)
    README_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.session:
        print(
            "Set GITHUB_USER_SESSION to your github.com user_session cookie.\n"
            "In DevTools → Application → Cookies → github.com → user_session.",
            file=sys.stderr,
        )
        return 1

    session = requests.Session()
    session.headers.update({"User-Agent": "movienet-scene-segmentation-readme-upload"})
    session.cookies.set("user_session", args.session, domain="github.com")
    session.cookies.set("__Host-user_session_same_site", args.session, domain="github.com")

    asset_url = upload_video(
        session,
        owner=args.owner,
        repo=args.repo,
        video_path=args.video.resolve(),
    )
    print(asset_url)

    if args.update_readme:
        patch_readme(asset_url)
        print(f"Updated {README_PATH.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
