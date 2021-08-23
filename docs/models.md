---
layout: default
---

[[back]](index.html)

# Models

## Finnish TDT latest (v2.7)

The latest Finnish TDT model trained on UD_Finnish-TDT v2.7 is available here: [models_fi_tdt_dia.tgz](http://dl.turkunlp.org/turku-parser-models/models_fi_tdt_dia.tgz)

Evaluation results on UD_Finnish-TDT test section with predicted segmentation:

```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |     99.72 |     99.66 |     99.69 |
Sentences  |     88.18 |     84.89 |     86.50 |
Words      |     99.72 |     99.64 |     99.68 |
UPOS       |     98.30 |     98.23 |     98.26 |     98.58
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |     96.59 |     96.52 |     96.55 |     96.86
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     96.30 |     96.23 |     96.26 |     96.57
UAS        |     93.59 |     93.52 |     93.55 |     93.86
LAS        |     92.24 |     92.17 |     92.21 |     92.50
CLAS       |     91.55 |     91.38 |     91.47 |     91.69
MLAS       |     87.09 |     86.93 |     87.01 |     87.22
BLEX       |     87.55 |     87.39 |     87.47 |     87.68
```

## English EWT latest (v2.7)

The latest English EWT model trained on UD_English-EWT v2.7 is upcoming

Evaluation results on UD_English-EWT test section with predicted segmentation:
```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |     98.96 |     99.05 |     99.00 |
Sentences  |     89.57 |     82.72 |     86.01 |
Words      |     98.85 |     98.92 |     98.88 |
UPOS       |     95.99 |     96.07 |     96.03 |     97.11
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |     96.37 |     96.45 |     96.41 |     97.49
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     97.34 |     97.42 |     97.38 |     98.48
UAS        |     89.41 |     89.48 |     89.44 |     90.45
LAS        |     87.30 |     87.37 |     87.33 |     88.32
CLAS       |     84.81 |     84.74 |     84.78 |     85.80
MLAS       |     80.26 |     80.19 |     80.22 |     81.19
BLEX       |     83.32 |     83.25 |     83.28 |     84.29
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
