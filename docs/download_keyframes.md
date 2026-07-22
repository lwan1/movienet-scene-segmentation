# Downloading MovieNet keyframes

The 318-movie 240p keyframe subset (~50 GB zipped, ~50 GB extracted) is hosted on Hugging Face:

**[asmith06/movienet318-keyframes-240p](https://huggingface.co/datasets/asmith06/movienet318-keyframes-240p)**

Both notebooks download and extract this archive automatically when you run the **Download & extract keyframes** cell.

## Automatic (notebooks)

1. Clone the repo and open a notebook.
2. Run the setup cells in order (repo clone → `pip install` → keyframes download).
3. On first run, the notebook downloads `keyframes_240p.zip` and extracts to `data/keyframes_240p/`.

## Manual download (CLI)

```bash
pip install -U "huggingface_hub[cli]" hf_xet
export HF_XET_HIGH_PERFORMANCE=1   # Git Bash / Linux / macOS

hf download asmith06/movienet318-keyframes-240p keyframes_240p.zip \
  --repo-type dataset \
  --local-dir data/

python scripts/setup_keyframes.py
```

## Already have the zip locally?

If `data/keyframes_240p.zip` already exists, the notebook skips the Hugging Face download and only extracts:

```bash
python scripts/setup_keyframes.py
```

## Full MovieNet archive (optional)

If you need the complete MovieNet keyframe corpus (~178 GB), use the community mirror [ZhengPeng7/MovieNet](https://huggingface.co/datasets/ZhengPeng7/MovieNet) and extract the 318-movie subset:

```bash
python scripts/download_movienet_keyframes_hf.py --local-dir ./hf_parts
cd hf_parts && cat frames_part_* > frames.zip

python scripts/extract_keyframes318.py \
  --zip-path ./hf_parts/frames.zip \
  --zip-prefix frames/ \
  --out-dir data/keyframes_240p
```

## Storage tips (Colab / limited disk)

- Colab free tier has ~100 GB disk — enough for the 50 GB zip plus extraction if you delete the zip after extracting.
- For a quick smoke test, set `LIMIT_MOVIES = 10` or `LIMIT_PER_SPLIT = 3` in the notebook before embedding/training cells.

## License

This keyframe subset is derived from [MovieNet](https://movienet.github.io/) and is intended for **academic research only**. See the dataset card on Hugging Face for usage terms.
