# Concurrent PCC cognitive-screening baseline

**Task:** classify the study's MoCA screening label among PCC records at the same visit. Positive means MoCA < 26; this is not a clinical diagnosis.  
**Data:** Dryad dataset `10.5061/dryad.kkwh70s9g`; checksum recorded in [`dataset-audit.md`](dataset-audit.md).  
**Labeled cohort:** 88 PCC records (36 positive, 52 negative; one PCC MoCA score missing and excluded).

## Protocol

- Compare a majority-class reference, DMI-only logistic regression, age/sex-only logistic regression, and DMI plus age/sex logistic regression.
- MRI features are the six predeclared whole-brain DMI measures: total gray/white matter V-extra, V-CSF, and V-intra.
- Age categories and sex are one-hot encoded. Numeric features are median-imputed and standardized inside each training fold. The MoCA score is used only to make the label and is excluded from predictors.
- Use L2 logistic regression with fixed `C=1`, no tuning, and a fixed 0.5 probability threshold for threshold metrics.
- Evaluation uses 5-fold stratified CV repeated 10 times (50 folds, seed 2026). Report mean and standard deviation across folds; overlapping folds make this descriptive variability, not an independent confidence interval.

## Exploratory results

| Model | ROC-AUC | Balanced accuracy | Sensitivity | Specificity | Brier score |
| --- | ---: | ---: | ---: | ---: | ---: |
| Majority baseline | 0.500 | 0.500 | 0.000 | 1.000 | 0.242 |
| Six DMI features | 0.554 ± 0.120 | 0.552 ± 0.083 | 0.323 ± 0.124 | 0.781 ± 0.126 | 0.249 ± 0.030 |
| DMI + age/sex | 0.495 ± 0.110 | 0.530 ± 0.092 | 0.333 ± 0.144 | 0.726 ± 0.116 | 0.273 ± 0.032 |
| Age/sex only | 0.420 ± 0.106 | 0.453 ± 0.094 | 0.159 ± 0.141 | 0.748 ± 0.165 | 0.271 ± 0.023 |

Values are fold mean ± fold SD except the deterministic majority reference. At the fixed 0.5 threshold, the DMI-only model has low sensitivity (about 0.32). Adding age and sex did not improve mean ROC-AUC in this run. These results are weak and variable; they do not support clinical screening use or future-cognition prediction.

## Limitations and next checks

- Only 88 labeled PCC records are available, compared with 6 MRI features in this first model and 701 candidate fields in the combined sheet. The wider table is not used because the sample is too small for unconstrained feature selection.
- The workbook has no participant ID, so independent subject-level split verification is unavailable. The study describes one scan per participant; the report should retain this limitation.
- The MoCA cutoff is a screening label, not a diagnosis. One PCC record is excluded for missing MoCA. Performance is internal and exploratory; no independent cohort has been tested.
- Next, inspect fold-level stability and calibration, predefine an appropriate sensitivity-focused operating point without reusing evaluation data, and obtain an independent cohort before making any generalization claim.

## Reproduce

Install `requirements-model.txt`, place the licensed workbook at `data/raw/Dryad_final.xlsx`, then run:

```sh
python scripts/train_screening_baseline.py
```

The aggregate JSON goes to `reports/generated/screening_baseline.json` and is git-ignored. No row-level predictions or trained model are saved.
