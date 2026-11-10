# Early Diagnosis and Cognitive Outcome Prediction of Post-Viral Neurological Syndromes Using Brain MRI Analysis

This repository contains the project presentation and supporting material for a proposed MRI-based research workflow for early identification of post-viral neurological changes and prediction of later cognitive outcomes.

## Project contents

- `presentation/post_viral_mri_research_template_final.pptx` — final presentation.
- `data/README.md` — candidate dataset provenance and audit status.
- `scripts/audit_dataset.py` — local, aggregate-only workbook audit; participant data remain local.
- `scripts/train_screening_baseline.py` — exploratory repeated-CV screening baseline.
- `scripts/evaluate_threshold_calibration.py` — nested threshold selection and calibration summary.

The presentation covers the motivation, literature survey, recent research progress, research gap, objectives, proposed technical workflow, candidate training data sources, iteration and evaluation plan, conclusion, and references. It presents a research proposal; it does not report a clinically validated diagnostic system or completed model results.

## Project team

- **Researchers:** Abhinav Kr Srivastava (2023UG1070), Aishwary Dixit (2023UG1049)
- **Faculty advisor:** Dr. Dhiran Kumar Mahto

## Topic

The project explores how brain MRI features, combined with clinical and cognitive assessment data, could support early risk estimation and follow-up planning for post-viral neurological syndromes. Any future model would require appropriate clinical validation before use in care.

## Data audit

The candidate Dryad dataset and local audit instructions are documented in [`data/README.md`](data/README.md). Download the workbook through Dryad and run the schema audit locally; the participant-level workbook is excluded from version control.

The completed source and workbook findings are summarized in [`reports/dataset-audit.md`](reports/dataset-audit.md).

The first baseline protocol and aggregate results are in [`reports/screening-baseline.md`](reports/screening-baseline.md). To reproduce it locally, install `requirements-model.txt` and run `python scripts/train_screening_baseline.py`.

The sensitivity-targeted threshold and calibration analysis is documented in [`reports/threshold-calibration.md`](reports/threshold-calibration.md). It uses nested cross-validation so each evaluated fold is held out from threshold selection.
