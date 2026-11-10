# Dataset provenance and handling

## Candidate dataset

- **Source:** Hosp et al., *Cerebral microstructural alterations in Post-COVID-condition are related to cognitive impairment, olfactory dysfunction, and fatigue* [Dryad dataset](https://doi.org/10.5061/dryad.kkwh70s9g).
- **Public files listed by Dryad:** `Dryad_final.xlsx` (about 1.60 MB) and `README.md` (about 3.26 KB).
- **Verified mirror:** [Zenodo record 10823138](https://zenodo.org/records/10823138) carries the same Dryad DOI and workbook. The downloaded workbook's SHA-256 (`d5488983c2e623bf7ee70640adb1d1f9e18b772c2fae3b9687e4f7587824b9af`) matches the checksum exposed by Dryad's file API. The workbook is stored locally at `data/raw/Dryad_final.xlsx` and is git-ignored.
- **Workbook contents described by Dryad:** demographics and clinical assessments (including MoCA), whole-brain gray/white matter diffusion microstructure metrics (V-extra, V-intra, V-CSF), FreeSurfer morphometry, and a combined sheet.
- **Published cohort counts:** 89 post-COVID-condition participants, 38 unimpaired post-COVID controls, and 46 healthy non-COVID controls. The article reports impaired MoCA in 41% of the post-COVID-condition group, using MoCA < 26 as its study cutoff.
- **Timing:** the dataset describes a prospective, single-visit cohort imaged about nine months after PCR positivity; it does not provide the earlier-MRI/later-cognition pairs required for future-outcome prediction.
- **Raw scans:** not included in the public dataset; the authors state that raw MRI may be requested from the corresponding author.

## Audit status (2026-11-10)

The source record and data dictionary were reviewed, and a structural audit was run on the checksum-matched workbook. The alternate Figshare link supplied for this audit was rejected: its article metadata and workbook describe rat intestinal ischemia/reperfusion data, not post-COVID MRI. It was not added to the project.

### Workbook-level findings

- Four sheets contain 173 data rows each: Demographic and Clinical Data (20 columns), DMI-Data (6), Freesurfer Data (675), and Combined (701).
- The `group` field has 89 PCC, 38 UPC, and 46 HNC records. All three source sheets match the Combined sheet row-for-row across 121,273 shared cells, with no mismatches; there is no explicit participant ID for independent identity checks.
- There are 8 exact duplicate rows in Demographic and Clinical Data. Because ages are grouped and no participant ID is provided, these may be distinct participants with identical recorded values; do not drop them as duplicate people.
- MoCA is missing in 47/173 records. In PCC, 36 records have MoCA <26, 52 have MoCA >=26, and 1 is missing. All 46 HNC records have MoCA missing. UPC has 7 MoCA scores <26 despite the cohort label, so do not substitute the cohort label for the cognitive label or pool groups without a prespecified analysis.
- The FreeSurfer and DMI fields have no missing values. Missingness is concentrated in clinical/questionnaire fields: `comorbidities` is missing in 90/173 records, GDS in 53/173, WEIMuS measures in 52/173, and MoCA in 47/173.
- The combined sheet has 701 fields, while only 88 PCC records have a MoCA label (36 below and 52 at/above the study cutoff). This is a high-dimensional, small-sample setting. Use a small prespecified feature set and regularization; do not train an unconstrained image/deep model on this table.
- MoCA <26 is the study's screening cutoff, not a clinical diagnosis. The source is cross-sectional, so it does not provide future cognitive outcomes.
- The public record describes a cross-sectional source. It can support evaluation of **concurrent cognitive screening**, subject to task/label review. It does not establish a longitudinal prediction task.

## Local audit

Install the audit dependency from `requirements-audit.txt`, download the workbook from the Dryad record, and run:

```sh
python scripts/audit_dataset.py data/raw/Dryad_final.xlsx
```

The report contains workbook/sheet dimensions, field names, missingness, numeric ranges, possible participant-key duplication counts, MoCA threshold counts by cohort, and row-wise source-to-combined comparisons. It does not write participant-level values. Generated output goes to `reports/generated/` and is git-ignored. See [`reports/dataset-audit.md`](../reports/dataset-audit.md) for a tracked summary.
