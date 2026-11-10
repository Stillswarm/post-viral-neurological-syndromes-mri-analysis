# Dataset provenance and handling

## Candidate dataset

- **Source:** Hosp et al., *Cerebral microstructural alterations in Post-COVID-condition are related to cognitive impairment, olfactory dysfunction, and fatigue* [Dryad dataset](https://doi.org/10.5061/dryad.kkwh70s9g).
- **Public files listed by Dryad:** `Dryad_final.xlsx` (about 1.60 MB) and `README.md` (about 3.26 KB).
- **Workbook contents described by Dryad:** demographics and clinical assessments (including MoCA), whole-brain gray/white matter diffusion microstructure metrics (V-extra, V-intra, V-CSF), FreeSurfer morphometry, and a combined sheet.
- **Published cohort counts:** 89 post-COVID-condition participants, 38 unimpaired post-COVID controls, and 46 healthy non-COVID controls. The article reports impaired MoCA in 41% of the post-COVID-condition group, using MoCA < 26 as its study cutoff.
- **Timing:** the dataset describes a prospective, single-visit cohort imaged about nine months after PCR positivity; it does not provide the earlier-MRI/later-cognition pairs required for future-outcome prediction.
- **Raw scans:** not included in the public dataset; the authors state that raw MRI may be requested from the corresponding author.

## Audit status (2026-11-10)

The source record and its data dictionary were reviewed. A row-level workbook audit is pending: Dryad lists the workbook, but its file download returned HTTP 401/403 in this environment. Once obtained through the normal Dryad download flow, save it as `data/raw/Dryad_final.xlsx` and run the local audit script. The workbook is intentionally excluded from Git.

The public record describes a cross-sectional source. It can be evaluated for a **concurrent cognitive-screening** pilot, subject to checking actual sheet structure, completeness, and labels. It does not establish a longitudinal prediction task. Because the cohort is small and the MoCA-impaired subgroup is a minority, model results should be treated as exploratory.

## Local audit

Install the audit dependency from `requirements-audit.txt`, download the workbook from the Dryad record, and run:

```sh
python scripts/audit_dataset.py data/raw/Dryad_final.xlsx
```

The report contains workbook/sheet dimensions, field names, missingness, numeric ranges, possible participant-key duplication counts, and MoCA threshold counts. It does not write participant-level values. Generated output goes to `reports/generated/` and is git-ignored.
