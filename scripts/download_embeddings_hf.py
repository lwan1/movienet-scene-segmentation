#!/usr/bin/env python3
"""Download precomputed MovieNet-318 embeddings from Hugging Face.

Dataset: https://huggingface.co/datasets/asmith06/scene-segmentation-embeddings

Uses the ``huggingface_hub`` Python API (not the ``hf`` CLI subprocess) so downloads
terminate reliably in Colab/Jupyter and show progress via tqdm.

Examples:
  python scripts/download_embeddings_hf.py
  python scripts/download_embeddings_hf.py --movie-ids tt0047396 tt0086190
  python scripts/download_embeddings_hf.py --modalities visual --movie-ids tt0047396
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        help="Download only these movie IDs. Default: all files under --modalities.",
    )
    parser.add_argument("--max-workers", type=int, default=8, help="Parallel download threads")
    parser.add_argument("--skip-install", action="store_true")
    return parser.parse_args()


def _ensure_hub() -> None:
    try:
        import huggingface_hub  # noqa: F401
    except ImportError:
        import subprocess

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "huggingface_hub[cli]", "hf_xet", "tqdm"],
            check=True,
        )


def _download_files(
    repo: str,
    local_dir: Path,
    remote_paths: list[str],
    max_workers: int,
) -> None:
    from huggingface_hub import hf_hub_download
    from tqdm import tqdm

    local_dir.mkdir(parents=True, exist_ok=True)

    def fetch(remote_path: str) -> str:
        return hf_hub_download(
            repo_id=repo,
            filename=remote_path,
            repo_type="dataset",
            local_dir=str(local_dir),
        )

    if len(remote_paths) == 1:
        fetch(remote_paths[0])
        return

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch, path): path for path in remote_paths}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading embeddings"):
            future.result()


def download_embeddings(
    repo: str,
    local_dir: Path,
    *,
    movie_ids: list[str] | None = None,
    modalities: tuple[str, ...] | list[str] = DEFAULT_MODALITIES,
    max_workers: int = 8,
) -> None:
    """Download embeddings into ``local_dir/{modality}/ttXXXX.npz``."""
    from huggingface_hub import snapshot_download

    os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "1")
    local_dir = local_dir.resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    modalities = tuple(modalities)

    print(f"Repo: https://huggingface.co/datasets/{repo}")
    print(f"Destination: {local_dir}")

    if movie_ids:
        remote_paths = [f"{mod}/{mid}.npz" for mid in movie_ids for mod in modalities]
        print(f"Fetching {len(remote_paths)} files ({len(movie_ids)} movies x {len(modalities)} modalities)...")
        _download_files(repo, local_dir, remote_paths, max_workers)
        return

    patterns = [f"{mod}/*" for mod in modalities]
    print(f"Snapshot download ({', '.join(patterns)})...")
    snapshot_download(
        repo_id=repo,
        repo_type="dataset",
        local_dir=str(local_dir),
        allow_patterns=patterns,
    )


def main() -> None:
    args = parse_args()
    if not args.skip_install:
        _ensure_hub()
    else:
        _ensure_hub()

    download_embeddings(
        args.repo,
        args.local_dir,
        movie_ids=args.movie_ids,
        modalities=args.modalities,
        max_workers=args.max_workers,
    )

    for mod in args.modalities:
        mod_dir = args.local_dir / mod
        n = len(list(mod_dir.glob("*.npz"))) if mod_dir.exists() else 0
        print(f"  {mod}/: {n} files")
    print("Done.")


if __name__ == "__main__":
    main()
