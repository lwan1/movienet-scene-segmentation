"""Extract MovieNet 240P keyframes for the MovieNet-318 scene-seg subset."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path


def load_movie_ids(split_path: Path) -> list[str]:
    with split_path.open(encoding="utf-8") as f:
        split = json.load(f)
    return split["train"] + split["val"] + split["test"]


def discover_split_path(project_root: Path) -> Path:
    matches = sorted(project_root.glob("**/scene318/meta/split318.json"))
    if not matches:
        matches = sorted(project_root.glob("**/split318.json"))
    if not matches:
        raise FileNotFoundError("Could not find split318.json under project root.")
    return matches[0]


def extract_keyframes_subset(
    zip_path: Path,
    split_path: Path,
    out_dir: Path,
    *,
    zip_prefix: str = "frames/",
    write_manifest: bool = True,
) -> tuple[int, list[str]]:
    """Extract keyframes for all movies in split318.

    Returns (folder_count, missing_movie_ids).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    movie_ids = load_movie_ids(split_path)
    movie_id_set = set(movie_ids)

    if len(movie_ids) != len(movie_id_set):
        raise ValueError(f"split318 must contain unique movie IDs; got {len(movie_ids)} entries.")

    paths_by_movie: dict[str, list[str]] = {mid: [] for mid in movie_ids}

    print(f"Indexing archive entries in {zip_path} ...")
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.startswith(zip_prefix) or name.endswith("/"):
                continue
            parts = name.split("/")
            if len(parts) < 3:
                continue
            movie_id = parts[1]
            if movie_id not in movie_id_set:
                continue
            paths_by_movie[movie_id].append(name)

        missing = [mid for mid in movie_ids if not paths_by_movie[mid]]
        if missing:
            print(f"Warning: {len(missing)} movies have no keyframes in the archive.")

        print(f"Extracting keyframes for {len(movie_ids) - len(missing)} movies to {out_dir} ...")
        extracted_folders = 0
        for i, movie_id in enumerate(movie_ids, start=1):
            entries = paths_by_movie[movie_id]
            if not entries:
                continue
            movie_dir = out_dir / movie_id
            movie_dir.mkdir(parents=True, exist_ok=True)
            for arcname in entries:
                filename = Path(arcname).name
                dest = movie_dir / filename
                if dest.exists():
                    continue
                with zf.open(arcname) as src, dest.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
            extracted_folders += 1
            if i % 10 == 0 or i == len(movie_ids):
                print(f"  [{i}/{len(movie_ids)}] {movie_id} ({len(entries)} files)")

    if write_manifest:
        write_extraction_manifest(out_dir, split_path, movie_ids, missing)

    return extracted_folders, missing


def write_extraction_manifest(
    out_dir: Path,
    split_path: Path,
    movie_ids: list[str],
    missing: list[str],
) -> None:
    with split_path.open(encoding="utf-8") as f:
        split = json.load(f)

    split_by_id = {
        movie_id: split_name
        for split_name in ("train", "val", "test")
        for movie_id in split[split_name]
    }
    missing_set = set(missing)
    manifest_path = out_dir / "manifest318.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        f.write("movie_id,split,file_count,extracted\n")
        for movie_id in movie_ids:
            movie_dir = out_dir / movie_id
            file_count = len(list(movie_dir.glob("*.jpg"))) if movie_dir.exists() else 0
            extracted = movie_id not in missing_set and file_count > 0
            f.write(f"{movie_id},{split_by_id[movie_id]},{file_count},{int(extracted)}\n")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=project_root / "movienet_keyframes_parts" / "frames.zip",
        help="Path to combined MovieNet frames.zip",
    )
    parser.add_argument(
        "--split-path",
        type=Path,
        default=None,
        help="Path to split318.json (auto-discovered if omitted)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=project_root / "keyframes_240p",
        help="Output directory (one ttXXXX folder per movie)",
    )
    parser.add_argument(
        "--zip-prefix",
        type=str,
        default="frames/",
        help="Top-level folder prefix inside the zip archive",
    )
    args = parser.parse_args()

    split_path = args.split_path or discover_split_path(project_root)
    extracted, missing = extract_keyframes_subset(
        zip_path=args.zip_path,
        split_path=split_path,
        out_dir=args.out_dir,
        zip_prefix=args.zip_prefix,
    )

    folder_count = len([p for p in args.out_dir.iterdir() if p.is_dir() and p.name.startswith("tt")])
    print(f"Extracted {extracted} movie folders ({folder_count} tt* dirs under {args.out_dir.resolve()})")
    if missing:
        print(f"Missing {len(missing)} movies: {missing}")
    if folder_count != 318:
        raise SystemExit(f"Expected 318 movie folders, found {folder_count}.")


if __name__ == "__main__":
    main()
