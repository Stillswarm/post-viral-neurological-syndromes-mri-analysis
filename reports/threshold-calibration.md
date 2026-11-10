# Threshold selection and calibration check

**Model:** L2 logistic regression using six prespecified whole-brain DMI measures.  
**Task:** concurrent MoCA < 26 screening among PCC records (n=88; 36 positive, 52 negative).  
**Protocol:** 5 outer stratified folds repeated 10 times; each outer training set uses 4-fold cross-validated probabilities to select the highest threshold achieving at least 0.80 sensitivity. The chosen threshold is then evaluated on that outer fold. Seed 2026.

The 0.80 sensitivity target is an exploratory analysis choice, not a clinically approved screening requirement. Threshold selection uses only each outer training fold; test-fold labels are not used to select the threshold.

## Results

| Measure | Mean ± SD |
| --- | ---: |
| Selected threshold | 0.275 ± 0.037 (range 0.173–0.349) |
| Outer-fold sensitivity | 0.816 ± 0.166 |
| Outer-fold specificity | 0.137 ± 0.130 |
| Outer-fold balanced accuracy | 0.477 ± 0.080 |
| Outer-fold ROC-AUC | 0.554 ± 0.120 |
| Brier score, pooled out-of-fold predictions per repeat | 0.249 ± 0.008 |
| Mean predicted risk minus observed rate | +0.009 ± 0.006 |
| Four-bin expected calibration error | 0.082 ± 0.023 |

The threshold rule reaches the requested sensitivity on average, at the cost of very low specificity. This would create many false positive flags in a screening setting. The DMI model's Brier score is slightly worse than the majority reference (0.242) from the first baseline. Mean calibration-in-the-large is close to zero, but the four-bin error and low discrimination show that the probabilities are not reliable enough for use as individual risk estimates.

## Interpretation and next step

Fold SDs describe variation across overlapping resamples; they are not confidence intervals. The 0.80 target itself needs clinical stakeholder input before it could guide a real screening policy. The current dataset is cross-sectional and has no participant ID, and no independent cohort has been tested. This analysis supports stopping short of deployment claims. The next research milestone is to locate an independent cohort with baseline MRI and later cognitive assessment, verify its access terms and label timing, then define a held-out validation plan before training a future-outcome model.

## Reproduce

Install `requirements-model.txt`, place the Dryad workbook at `data/raw/Dryad_final.xlsx`, and run:

```sh
python scripts/evaluate_threshold_calibration.py
```

Aggregate output is written locally to `reports/generated/threshold_calibration.json` and is git-ignored. No fitted model or row-level predictions are saved.
