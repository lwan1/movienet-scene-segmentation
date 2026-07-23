#!/usr/bin/env python3
"""Download precomputed MovieNet-318 embeddings from Hugging Face.

Dataset: https://huggingface.co/datasets/asmith06/scene-segmentation-embeddings

Layout mirrors ``data/embeddings/`` (visual/, subtitle/, multimodal/, …).

Examples:
  python scripts/download_embeddings_hf.py
  python scripts/download_embeddings_hf.py --movie-ids tt0047396 tt0086190
  python scripts/download_embeddings_hf.py --modalities visual --movie-ids tt0047396
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HF_REPO = "asmith06/scene-segmentation-embeddings"
DEFAULT_MODALITIES = ("visual", "subtitle", "multimodal")


def load_hf_repo(config_path: Path) -> str:
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8")).get(
            "hf_embeddings_repo", DEFAULT_HF_REPO
        )
    return DEFAULT_HF_REPO


def hf_bin() -> str:
    for name in ("hf", "huggingface-cli"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("Install huggingface_hub CLI: pip install 'huggingface_hub[cli]'")


def download_file(hf: str, repo: str, remote_path: str, local_dir: Path) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            hf,
            "download",
            repo,
            remote_path,
            "--repo-type",
            "dataset",
            "--local-dir",
            str(local_dir),
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    config_path = REPO_ROOT / "checkpoints" / "bassl" / "inference_config.json"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--repo",
        default=load_hf_repo(config_path),
        help=f"Hugging Face dataset repo (default: {DEFAULT_HF_REPO})",
    )
    parser.add_argument(
        "--local-dir",
        type=Path,
        default=REPO_ROOT / "data" / "embeddings",
        help="Output directory (becomes data/embeddings/)",
    )
    parser.add_argument(
        "--modalities",
        nargs="+",
        default=list(DEFAULT_MODALITIES),
        choices=list(DEFAULT_MODALITIES),
    )
    parser.add_argument(
        "--movie-ids",
        nargs="+",
        default=None,
        help="Download only these movie IDs (smoke tests). Default: full dataset.",
    )
    parser.add_argument("--skip-install", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.skip_install:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "huggingface_hub[cli]", "hf_xet"],
            check=True,
        )

    hf = hf_bin()
    import os

    os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "1")
    local_dir = args.local_dir.resolve()
    print(f"Repo: https://huggingface.co/datasets/{args.repo}")
    print(f"Destination: {local_dir}")

    if args.movie_ids:
        for movie_id in args.movie_ids:
            for modality in args.modalities:
                remote = f"{modality}/{movie_id}.npz"
                print(f"  {remote}")
                download_file(hf, args.repo, remote, local_dir)
        print(f"Downloaded {len(args.movie_ids)} movies x {len(args.modalities)} modalities.")
        return

    print("Downloading full embedding dataset (~3 GB)...")
    subprocess.run(
        [hf, "download", args.repo, "--repo-type", "dataset", "--local-dir", str(local_dir)],
        check=True,
    )
    n_visual = len(list((local_dir / "visual").glob("*.npz"))) if (local_dir / "visual").exists() else 0
    print(f"Done. visual/*.npz count: {n_visual}")


if __name__ == "__main__":
    main()
