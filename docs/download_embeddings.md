# Downloading precomputed embeddings

Precomputed MovieNet-318 shot embeddings (~3 GB) are hosted on Hugging Face:

**[asmith06/scene-segmentation-embeddings](https://huggingface.co/datasets/asmith06/scene-segmentation-embeddings)**

The dataset layout matches the local `data/embeddings/` directory:

```
data/embeddings/
├── visual/       # CLIP ViT-B/32 (512-d)
├── subtitle/     # MiniLM-L6-v2
├── multimodal/   # concat(visual, subtitle), L2-normalized
└── ttXXXX.npz    # legacy root-level files (optional)
```

## Automatic (notebooks)

All three notebooks default to `DOWNLOAD_EMBEDDINGS = True` and `DOWNLOAD_KEYFRAMES = False` — the **T4-friendly path** on Colab.

1. Clone the repo and open a notebook.
2. Run setup cells through the asset download cell.
3. Embeddings are downloaded to `data/embeddings/` (no zip extraction).

## Manual download (CLI)

```bash
pip install -U "huggingface_hub[cli]" hf_xet
export HF_XET_HIGH_PERFORMANCE=1

# Full dataset (~3 GB)
python scripts/download_embeddings_hf.py

# Smoke test — single movie
python scripts/download_embeddings_hf.py --movie-ids tt0047396 --modalities visual subtitle multimodal
```

Uses the `huggingface_hub` Python API with parallel downloads and a tqdm progress bar (reliable in Colab; avoids hung `hf` CLI subprocesses).

Optional equivalent:

```bash
hf download asmith06/scene-segmentation-embeddings \
  --repo-type dataset \
  --local-dir data/embeddings
```

## Which modalities do I need?

| Notebook | Modality |
|----------|----------|
| `test_scene_seg_bassl_inference.ipynb` | `visual/` only |
| `test_scene_seg_bassl.ipynb` | `visual/` only |
| `test_keyframes.ipynb` | `visual/`, `subtitle/`, `multimodal/` |

## License

Embeddings are derived from [MovieNet](https://movienet.github.io/) keyframes and subtitles for **academic research only**.
