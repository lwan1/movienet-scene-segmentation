"""Extract MovieNet-318 keyframes from a local zip into data/keyframes_240p/."""

from __future__ import annotations

import argparse
from pathlib import Path

from extract_keyframes318 import discover_split_path, extract_keyframes_subset


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=repo_root / "data" / "keyframes_240p.zip",
        help="Path to keyframes_240p.zip (318-movie subset or full MovieNet archive)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "data" / "keyframes_240p",
        help="Output directory for extracted ttXXXX/ folders",
    )
    parser.add_argument(
        "--zip-prefix",
        type=str,
        default="keyframes_240p/",
        help="Top-level folder inside zip before ttXXXX/ (use '' if ttXXXX/ is at zip root)",
    )
    parser.add_argument(
        "--movie-ids",
        nargs="+",
        default=None,
        help="Extract only these movie IDs (T4 smoke tests)",
    )
    args = parser.parse_args()

    if not args.zip_path.exists():
        raise SystemExit(
            f"Keyframes zip not found: {args.zip_path}\n"
            "Place keyframes_240p.zip under data/ or pass --zip-path.\n"
            "See README.md for download instructions."
        )

    split_path = discover_split_path(repo_root)
    extracted, missing = extract_keyframes_subset(
        zip_path=args.zip_path,
        split_path=split_path,
        out_dir=args.out_dir,
        zip_prefix=args.zip_prefix,
        movie_ids=args.movie_ids,
        write_manifest=False,
    )
    folder_count = len([p for p in args.out_dir.iterdir() if p.is_dir() and p.name.startswith("tt")])
    print(f"Extracted {extracted} movies ({folder_count} tt* dirs) -> {args.out_dir.resolve()}")
    if missing:
        print(f"Missing keyframes for {len(missing)} movies: {missing[:10]}{'...' if len(missing) > 10 else ''}")


if __name__ == "__main__":
    main()
