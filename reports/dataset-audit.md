# Dataset audit: Dryad post-COVID MRI workbook

**Audit date:** 2026-11-10  
**Dataset:** Hosp et al., [Dryad DOI 10.5061/dryad.kkwh70s9g](https://doi.org/10.5061/dryad.kkwh70s9g)  
**Local file:** `data/raw/Dryad_final.xlsx` (excluded from Git)  
**SHA-256:** `d5488983c2e623bf7ee70640adb1d1f9e18b772c2fae3b9687e4f7587824b9af`

## Source verification

The Dryad file download was blocked in this environment, so the workbook was obtained from [Zenodo record 10823138](https://zenodo.org/records/10823138), which carries the same Dryad DOI and identifies the file as `Dryad_final.xlsx`. Its size and SHA-256 match the Dryad file API metadata. The workbook is CC0.

The [Figshare URL supplied as an alternative](https://figshare.com/articles/dataset/raw_data-Dryad_xlsx/24793380?file=43606320) was checked and rejected. Its Figshare record DOI is `10.6084/m9.figshare.24793380.v1`; the record describes rat intestinal ischemia/reperfusion experiments, and the downloadable workbook has blood/organ measurements. It is not the post-COVID MRI dataset and is not used in this project.

## Structural and completeness results

| Sheet | Rows | Columns | Finding |
| --- | ---: | ---: | --- |
| Demographic and Clinical Data | 173 | 20 | Includes group and MoCA; 8 exact repeated rows |
| DMI-Data | 173 | 6 | No missing values |
| Freesurfer Data | 173 | 675 | No missing values |
| Combined | 173 | 701 | Clinical missingness retained |

The group counts are PCC 89, UPC 38, and HNC 46. Each separate source sheet matches its corresponding fields in Combined row-by-row: 121,273 cell comparisons, zero mismatches. The workbook contains no explicit participant ID, so row alignment is consistent with the combined sheet but cannot be independently checked against an identity key. The 8 repeated clinical rows are not removed; grouped age and identical recorded characteristics can make different people indistinguishable.

MoCA availability and study-cutoff counts:

| Cohort | MoCA < 26 | MoCA >= 26 | Missing |
| --- | ---: | ---: | ---: |
| PCC | 36 | 52 | 1 |
| UPC | 7 | 31 | 0 |
| HNC | 0 | 0 | 46 |

The PCC screening pilot therefore has 88 labeled records, with 36 below and 52 at/above the source study's MoCA cutoff. The 46 HNC records cannot enter this MoCA-labeled task. Seven UPC records are below the cutoff, so group membership must not be treated as equivalent to cognitive status. MoCA <26 is a screening label in this analysis, not a diagnosis.

In the Combined sheet, MoCA is missing in 47/173 records, GDS in 53/173, WEIMuS subscales in 52/173, and comorbidities in 90/173. All 6 DMI metrics and 675 FreeSurfer variables are populated. No participant-level rows or values are included in this report.

## Implications for the first modeling task

- Treat this as concurrent cognitive screening in the PCC group, not prediction of later cognition.
- Start with 88 complete PCC cases and a small, prespecified MRI feature set. The 701-column combined table is far wider than this labeled subset.
- Exclude MoCA and any direct target-derived fields from predictors. Fit imputation, scaling, and feature selection within each training fold.
- Use a regularized, interpretable baseline and repeated stratified evaluation. Report uncertainty and label the result exploratory; it is not clinical validation.
- A future-cognition task needs a different dataset with baseline MRI and later cognitive testing.

## Reproduce the audit

Install `requirements-audit.txt`, obtain the workbook through the cited source, and run `python scripts/audit_dataset.py data/raw/Dryad_final.xlsx`. The JSON output is local-only at `reports/generated/dataset_audit.json` and is git-ignored.
