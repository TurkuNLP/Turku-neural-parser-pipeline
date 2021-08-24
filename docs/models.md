---
layout: default
---

[[back]](index.html)

# Models

## Finnish TDT latest (v2.8)

The latest Finnish TDT model trained on UD_Finnish-TDT v2.8 is available here: [models_fi_tdt_dia.tgz](http://dl.turkunlp.org/turku-parser-models/models_fi_tdt_dia.tgz)

Evaluation results on UD_Finnish-TDT test section with predicted segmentation:

```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |     99.72 |     99.66 |     99.69 |
Sentences  |     88.18 |     84.89 |     86.50 |
Words      |     99.72 |     99.64 |     99.68 |
UPOS       |     97.84 |     97.77 |     97.80 |     98.12
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |     96.46 |     96.39 |     96.42 |     96.73
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     96.17 |     96.10 |     96.13 |     96.44
UAS        |     92.93 |     92.87 |     92.90 |     93.20
LAS        |     91.27 |     91.21 |     91.24 |     91.53
CLAS       |     90.64 |     90.45 |     90.55 |     90.75
MLAS       |     85.63 |     85.44 |     85.53 |     85.73
BLEX       |     86.51 |     86.32 |     86.42 |     86.61
```

## English EWT latest (v2.8)

The latest English EWT model (general English) trained on UD_English-EWT v2.8 is available here: [models_en_ewt_dia.tgz](http://dl.turkunlp.org/turku-parser-models/models_en_ewt_dia.tgz)

Evaluation results on UD_English-EWT test section with predicted segmentation:
```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |     99.35 |     99.16 |     99.25 |
Sentences  |     88.36 |     83.29 |     85.75 |
Words      |     99.14 |     98.86 |     99.00 |
UPOS       |     95.45 |     95.19 |     95.32 |     96.28
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |     96.06 |     95.79 |     95.92 |     96.89
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     96.72 |     96.46 |     96.59 |     97.57
UAS        |     89.84 |     89.59 |     89.71 |     90.62
LAS        |     87.62 |     87.38 |     87.50 |     88.38
CLAS       |     84.99 |     84.76 |     84.88 |     85.76
MLAS       |     79.24 |     79.03 |     79.14 |     79.96
BLEX       |     82.34 |     82.13 |     82.23 |     83.09
```

## Biomedical English (CRAFT) <a id="craft"></a>

The Biomedical English model trained on CRAFT corpus v4.0.0 is upcoming

Evaluation results on test section with gold segmentation (more details in the paper link below):

```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |    100.00 |    100.00 |    100.00 |
Sentences  |    100.00 |    100.00 |    100.00 |
Words      |    100.00 |    100.00 |    100.00 |
UPOS       |     98.79 |     98.79 |     98.79 |     98.79
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |     98.79 |     98.79 |     98.79 |     98.79
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     99.43 |     99.43 |     99.43 |     99.43
UAS        |     93.45 |     93.45 |     93.45 |     93.45
LAS        |     92.31 |     92.31 |     92.31 |     92.31
CLAS       |     90.18 |     89.90 |     90.04 |     89.90
MLAS       |     88.36 |     88.09 |     88.22 |     88.09
BLEX       |     89.46 |     89.18 |     89.32 |     89.18
```

Reference and more details:
```
@article{kanerva2020dependency,
  title={Dependency parsing of biomedical text with {BERT}},
  author={Kanerva, Jenna and Ginter, Filip and Pyysalo, Sampo},
  journal={BMC Bioinformatics},
  volume={21},
  number={23},
  pages={1--12},
  year={2020},
  publisher={Springer},
  url={https://doi.org/10.1186/s12859-020-03905-8},
}
```
