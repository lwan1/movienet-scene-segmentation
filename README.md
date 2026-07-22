# MovieNet-318 Scene Segmentation

Reproducible notebooks for **movie scene boundary detection** on the [MovieNet-318](https://movienet.github.io/projects/cvpr20sceneseg.html) benchmark (190 train / 64 val / 64 test movies).

This repository contains labels, splits, shot timing, subtitles, and two end-to-end pipelines:

| Notebook | Description |
|----------|-------------|
| [`notebooks/test_keyframes.ipynb`](notebooks/test_keyframes.ipynb) | Clustering baselines with subtitle (MiniLM), visual (CLIP), and multimodal embeddings |
| [`notebooks/test_scene_seg_bassl.ipynb`](notebooks/test_scene_seg_bassl.ipynb) | BaSSL-inspired SSL pretraining + boundary-head finetuning on frozen CLIP features |

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/movienet-scene-segmentation.git
cd movienet-scene-segmentation
pip install -r requirements.txt
```

### 2. Run a notebook (keyframes download automatically)

**Google Colab:** open either notebook, set `REPO_URL` in the setup cell to your fork, enable a GPU runtime, and run all cells. Keyframes are downloaded from Hugging Face on first run (~50 GB).

**Local Jupyter:**

```bash
jupyter notebook notebooks/test_keyframes.ipynb
```

Set `SCENE_SEG_REPO_DIR` to the repo root if the auto-detection cell does not find `data/scene318/`.

The notebooks download keyframes from **[asmith06/movienet318-keyframes-240p](https://huggingface.co/datasets/asmith06/movienet318-keyframes-240p)** and extract them to `data/keyframes_240p/`.

### Manual keyframe download (optional)

```bash
export HF_XET_HIGH_PERFORMANCE=1
hf download asmith06/movienet318-keyframes-240p keyframes_240p.zip \
  --repo-type dataset --local-dir data/
python scripts/setup_keyframes.py
```

See [`docs/download_keyframes.md`](docs/download_keyframes.md) for details and alternatives.

### Smoke test

In either notebook, set `LIMIT_MOVIES = 10` or `LIMIT_PER_SPLIT = 3` before the expensive embedding/training cells.

## Repository layout

```
movienet-scene-segmentation/
├── data/
│   ├── scene318/
│   │   ├── label318/          # per-movie scene boundary labels (318 files)
│   │   ├── meta/split318.json # official train/val/test split
│   │   └── shot_movie318/     # shot frame ranges for subtitle alignment
│   ├── subtitle/              # SRT files for 314/318 movies
│   ├── keyframes_240p.zip     # NOT in git — downloaded from Hugging Face
│   └── keyframes_240p/        # NOT in git — extracted keyframes
├── notebooks/
├── scripts/
├── outputs/                   # NOT in git — embeddings, checkpoints, results
└── requirements.txt
```

Manifest CSV files and other MovieNet metadata dumps are **intentionally excluded**; only files required to run the notebooks are included.

## Data license & usage

MovieNet data (labels, keyframes, subtitles) is for **academic research only**. Do not redistribute outside the terms of the [MovieNet project](https://movienet.github.io/). By using this repo you agree to cite the original papers below.

## Acknowledgements

This project builds on open research and tooling from:

- **MovieNet** — dataset annotations, keyframes, and the MovieNet-318 scene segmentation benchmark ([Huang et al., ECCV 2020](https://movienet.github.io/projects/eccv20movienet.html))
- **LGSS** — Local-to-Global Scene Segmentation baseline and label convention ([Rao et al., CVPR 2020](https://movienet.github.io/projects/cvpr20sceneseg.html))
- **BaSSL** — boundary-aware self-supervised learning for scene segmentation ([Mun et al., ACCV 2022](https://arxiv.org/abs/2201.05277))
- **CLIP** — visual embeddings ([Radford et al., ICML 2021](https://arxiv.org/abs/2103.00020))
- **Sentence-Transformers** — subtitle text embeddings ([Reimers & Gurevych, EMNLP 2019](https://arxiv.org/abs/1908.10084))
- **MovieNet-318 keyframes on Hugging Face** — [asmith06/movienet318-keyframes-240p](https://huggingface.co/datasets/asmith06/movienet318-keyframes-240p)

Published reference numbers in the notebooks (TranS4mer, MEGA, Scene-VLM) are taken from recent literature surveys on MovieNet-318; see those papers for their experimental settings.

## Citations

If you use this code or the MovieNet-318 benchmark, please cite:

```bibtex
@inproceedings{huang2020movienet,
  title={MovieNet: A Holistic Dataset for Movie Understanding},
  author={Huang, Qingqiu and Xiong, Yu and Rao, Anyi and Wang, Jiaze and Lin, Dahua},
  booktitle={European Conference on Computer Vision (ECCV)},
  year={2020}
}

@inproceedings{rao2020local,
  title={A Local-to-Global Approach to Multi-Modal Movie Scene Segmentation},
  author={Rao, Anyi and Xu, Linning and Xiong, Yu and Xu, Guodong and Huang, Qingqiu and Zhou, Bolei and Lin, Dahua},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages={10146--10155},
  year={2020}
}

@inproceedings{mun2022bassl,
  title={Boundary-aware Self-supervised Learning for Video Scene Segmentation},
  author={Mun, Seongho and Cho, Sunghyun and Han, Bohyung},
  booktitle={Proceedings of the Asian Conference on Computer Vision (ACCV)},
  year={2022}
}
```

## Publishing checklist

Before pushing to GitHub:

1. Replace `YOUR_USERNAME` in this README and in the notebook `REPO_URL` default.
2. Confirm `data/keyframes_240p/` and `*.zip` are gitignored (they are by default).
3. Optional: add a Colab badge linking to `notebooks/test_keyframes.ipynb` on GitHub.

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/movienet-scene-segmentation/blob/main/notebooks/test_keyframes.ipynb)
```
