# Candidate longitudinal cohort review

**Review date:** 2026-11-10  
**Purpose:** identify an independent cohort with baseline MRI and later cognitive assessment for future-outcome modeling.

## Recommended first candidate: Geneva COVID-COG

The [COVID-COG published data record](https://yareta.unige.ch/archives/4c1aa098-0b0a-4144-8e48-212f96b31574) describes neuropsychological, MRI, olfactory, and neurological assessments at 6–9 and 12–15 months after infection. A follow-up paper reports repeated neuropsychological assessments in 95 patients at those two time points. This matches the needed time direction better than the current Dryad cohort.

The public record lists 59 files (12.3 MB), a CC BY 4.0 license, and a separate **Contract on the use of data** indicator. The broader COVID-COG archive also has a restricted 56 GB folder. The public record does not establish which paired MRI and cognitive fields are in the 59-file published package or how many people have complete MRI and cognition at both visits. These points must be confirmed from the data dictionary and contract before any files are used. No data were downloaded and no contract was accepted in this review.

**Potential study design after access review:** use T1 MRI at 6–9 months to predict a prespecified T2 cognitive score at 12–15 months, adjusting for T1 cognition. Keep all visits from one participant together. First verify repeated MRI is available for the same participants; if only cognition repeats, the cohort cannot support the proposed MRI-based future-outcome task as specified.

## Alternative: UK Biobank COVID re-imaging

The UK Biobank COVID re-imaging study has pre-infection and post-infection imaging and repeated cognitive assessments. Its published analysis included 785 participants scanned twice, 401 of whom had SARS-CoV-2 infection between scans; it reported longitudinal changes in Trail Making scores. Source data are available through UK Biobank application, and the current UK Biobank imaging page lists COVID-19 repeat scans for a subgroup of 2,000 participants.

This is useful for studying infection-associated longitudinal MRI and cognition, but the community cohort is not a clinically defined post-COVID neurological syndrome cohort. It is also controlled access. Treat it as a secondary validation source only if approved access and the research question align.

## Concurrent-validation alternative: Graz Long-Covid-Cognition-fMRI

The [Mendeley Data record](https://data.mendeley.com/datasets/k3r47sp27r/3) provides a CC BY 4.0 dataset from a structural/resting-state MRI and neuropsychology study of Austrian Long-COVID patients. The public record establishes MRI and neuropsychology but does not establish repeated visits. Until its file dictionary confirms paired follow-up, treat it as a possible concurrent validation cohort, not a future-cognition dataset. Its imaging features may also differ from the six DMI predictors in the initial pilot.

## Decision and next actions

1. Review the COVID-COG data-use contract and verify whether use for this research is permitted.
2. Confirm the public package contains per-participant paired baseline MRI and follow-up cognitive outcomes, identify the common cognitive measures, and count complete cases.
3. If suitable, define the target as a continuous follow-up score adjusted for baseline score (or a prespecified change score), document attrition/missingness, and freeze a participant-level held-out validation plan before training.
4. If the public COVID-COG package lacks paired MRI or its contract does not permit use, pursue an authorized data request or a different cohort. Do not reuse the Dryad cross-sectional rows as a substitute for future outcomes.

No dataset was downloaded from these candidate cohorts. The existing Dryad workbook remains local and git-ignored.
