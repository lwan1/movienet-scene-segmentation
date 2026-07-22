#!/usr/bin/env python3
"""Download MovieNet 240P keyframe archive parts from Hugging Face at max speed.

Dataset: https://huggingface.co/datasets/ZhengPeng7/MovieNet/tree/main

Downloads ``frames_part_aa`` through ``frames_part_ai`` (~178 GB total) using the
official Hugging Face CLI (``hf download``) with Rust-accelerated parallel transfers.

Performance notes (huggingface_hub >= 1.0)
-----------------------------------------
``hf_transfer`` + ``HF_HUB_ENABLE_HF_TRANSFER=1`` is **deprecated** and ignored by
current ``huggingface_hub``. The official replacement is ``hf_xet`` with::

    HF_XET_HIGH_PERFORMANCE=1

This uses the same goal: parallel chunked downloads to saturate bandwidth. See:
https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables

Legacy mode (``--legacy-hf-transfer``) pins ``huggingface_hub<1.0`` and enables
``HF_HUB_ENABLE_HF_TRANSFER=1`` if you explicitly need the old stack.

Examples
--------
# Dry run (show commands only)
python scripts/download_movienet_keyframes_hf.py --dry-run

# Download all 9 parts to local folder (fast Xet mode, default)
python scripts/download_movienet_keyframes_hf.py --local-dir ./movienet_keyframes_parts

# Colab / Google Drive destination
python scripts/download_movienet_keyframes_hf.py \\
  --local-dir "/content/drive/MyDrive/Scene Segmentation/movienet_keyframes_parts"

# Download a single part first (smoke test)
python scripts/download_movienet_keyframes_hf.py --parts aa --local-dir ./parts

# After all parts download, combine into one zip (optional, needs ~178 GB free):
#   cat movienet_keyframes_parts/frames_part_* > frames.zip
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ID = "ZhengPeng7/MovieNet"
ALL_PARTS = [f"frames_part_{suffix}" for suffix in "aa ab ac ad ae af ag ah ai".split()]


def ensure_deps(legacy_hf_transfer: bool) -> None:
    if legacy_hf_transfer:
        packages = ["huggingface_hub[cli,hf_transfer]<1.0", "hf_transfer"]
    else:
        packages = ["huggingface_hub[cli]", "hf_xet"]
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-U", *packages],
        check=True,
    )


def hf_executable() -> str:
    hf = shutil.which("hf")
    if hf:
        return hf
    cli = shutil.which("huggingface-cli")
    if cli:
        return cli
    raise RuntimeError("Could not find `hf` or `huggingface-cli` after install.")


def build_env(legacy_hf_transfer: bool, token: str | None) -> dict[str, str]:
    env = os.environ.copy()
    if legacy_hf_transfer:
        env["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
        env.pop("HF_XET_HIGH_PERFORMANCE", None)
        print("Using legacy hf_transfer (huggingface_hub<1.0)")
    else:
        env["HF_XET_HIGH_PERFORMANCE"] = "1"
        print("Using hf_xet high-performance mode (HF_XET_HIGH_PERFORMANCE=1)")
    if token:
        env["HF_TOKEN"] = token
    elif env.get("HF_TOKEN") or env.get("HUGGING_FACE_HUB_TOKEN"):
        print("HF token found in environment (authenticated downloads)")
    else:
        print("No HF token set — public dataset download should still work")
    return env


def download_part(
    hf_bin: str,
    part: str,
    local_dir: Path,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        hf_bin,
        "download",
        REPO_ID,
        part,
        "--repo-type",
        "dataset",
        "--local-dir",
        str(local_dir),
    ]
    print("\n$ " + " ".join(cmd))
    if dry_run:
        return
    subprocess.run(cmd, env=env, check=True)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--local-dir",
        type=Path,
        default=root / "movienet_keyframes_parts",
        help="Directory for frames_part_aa ... frames_part_ai",
    )
    parser.add_argument(
        "--parts",
        nargs="+",
        default=ALL_PARTS,
        help=f"Subset of parts to download (default: all {len(ALL_PARTS)} parts)",
    )
    parser.add_argument(
        "--legacy-hf-transfer",
        action="store_true",
        help="Use deprecated hf_transfer + huggingface_hub<1.0 (not recommended on hub 1.x)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Hugging Face token (or set HF_TOKEN / huggingface-cli login)",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pip install of huggingface_hub / hf_xet",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without downloading",
    )
    return parser.parse_args()


def normalize_parts(requested: list[str]) -> list[str]:
    out: list[str] = []
    for p in requested:
        name = p if p.startswith("frames_part_") else f"frames_part_{p}"
        if name not in ALL_PARTS:
            raise ValueError(f"Unknown part {p!r}. Valid: {', '.join(ALL_PARTS)}")
        out.append(name)
    return out


def main() -> None:
    args = parse_args()
    parts = normalize_parts(args.parts)

    if not args.skip_install:
        print("Installing / upgrading Hugging Face CLI dependencies...")
        ensure_deps(args.legacy_hf_transfer)

    hf_bin = hf_executable()
    env = build_env(args.legacy_hf_transfer, args.token)
    local_dir = args.local_dir.resolve()
    print(f"Destination: {local_dir}")
    print(f"Parts ({len(parts)}): {', '.join(parts)}")
    print(f"Dataset: https://huggingface.co/datasets/{REPO_ID}")

    for i, part in enumerate(parts, 1):
        print(f"\n[{i}/{len(parts)}] {part}")
        download_part(hf_bin, part, local_dir, env, args.dry_run)

    if not args.dry_run:
        print("\nDownload complete.")
        print("Next steps (optional):")
        print(f"  1. Verify files in: {local_dir}")
        print("  2. Combine parts:  cat frames_part_* > frames.zip")
        print("  3. Selective extract for MovieNet-318:")
        print("     unzip frames.zip 'tt0047396/*' -d keyframes_240p/")
    else:
        print("\nDry run finished — no files downloaded.")


if __name__ == "__main__":
    main()
