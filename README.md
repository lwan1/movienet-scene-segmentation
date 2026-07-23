# Scene Segmentation

Reproducible notebooks for **movie scene boundary detection** on the [MovieNet-318](https://movienet.github.io/projects/cvpr20sceneseg.html) benchmark (190 train / 64 val / 64 test movies) and BBC Dataset (11 test movies).

This repository contains labels, splits, shot timing, subtitles, and end-to-end pipelines:

| Notebook | Description |
|----------|-------------|
| [`notebooks/unsupervised_approaches.ipynb`](notebooks/unsupervised_approaches.ipynb) | Comparsion of Adjacent Only w/ Priors on BBC |
| [`notebooks/test_keyframes.ipynb`](notebooks/test_keyframes.ipynb) | Clustering baselines with subtitle (MiniLM), visual (CLIP), and multimodal embeddings |
| [`notebooks/test_scene_seg_bassl.ipynb`](notebooks/test_scene_seg_bassl.ipynb) | BaSSL-inspired SSL pretraining + boundary-head finetuning on frozen CLIP features |
| [`notebooks/test_scene_seg_bassl_inference.ipynb`](notebooks/test_scene_seg_bassl_inference.ipynb) | **Inference only** — load shipped checkpoint + HF embeddings (~3 GB); skips keyframes & training |

## Demo

Sample **predicted scene boundaries** from the BaSSL-inspired pipeline on a MovieNet-318 clip. Each segment shows keyframes grouped by the model’s predicted scene cuts (see the visualization cells in [`test_scene_seg_bassl.ipynb`](notebooks/test_scene_seg_bassl.ipynb)). Example:


https://github.com/user-attachments/assets/3c5a533b-3e0a-4f62-b913-41ae00074a88



<p align="center"><em>Click the preview to open the full MP4 in GitHub’s built-in player.</em></p>

## Run in Colab

Enable a **GPU runtime** before running. Preferrably a G4 but suitable with a T4.

- **`unsupervised_approaches.ipynb`** — Comparison of Adjacent Only w/ Priors on BBC [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lwan1/movienet-scene-segmentation/blob/main/notebooks/unsupervised_approaches.ipynb)
- **`test_keyframes.ipynb`** — Clustering baselines with subtitle (MiniLM), visual (CLIP), and multimodal embeddings [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lwan1/movienet-scene-segmentation/blob/main/notebooks/test_keyframes.ipynb)
- **`test_scene_seg_bassl.ipynb`** — BaSSL-inspired SSL pretraining + boundary-head finetuning on frozen CLIP features [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lwan1/movienet-scene-segmentation/blob/main/notebooks/test_scene_seg_bassl.ipynb)
- **`test_scene_seg_bassl_inference.ipynb`** — Inference only: load shipped checkpoint + HF embeddings (~3 GB); skips keyframes & training [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lwan1/movienet-scene-segmentation/blob/main/notebooks/test_scene_seg_bassl_inference.ipynb)


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
- **MovieNet-318 precomputed embeddings** — [asmith06/scene-segmentation-embeddings](https://huggingface.co/datasets/asmith06/scene-segmentation-embeddings)

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
  title={BaSSL: Boundary-aware Self-Supervised Learning for Video Scene Segmentation},
  author={Mun, Jonghwan and Shin, Minchul and Han, Gunsoo and Lee, Sangho and Ha, Seongsu and Lee, Joonseok and Kim, Eun-Sol},
  booktitle={Proceedings of the Asian Conference on Computer Vision (ACCV)},
  pages={4027--4043},
  year={2022},
  url={https://arxiv.org/abs/2201.05277}
}
```

