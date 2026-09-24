# Replication and Release Notes

This file documents issues identified while preparing the uploaded HyRAG materials for public release. These notes are intentionally explicit so that the public repository does not silently claim reproducibility beyond what the supplied artifacts support.

## Corrections made in the cleaned notebook

The original uploaded notebook contained several code/data mismatches:

1. It loaded `Test_Dataset.csv`, but the supplied evaluation files are `Test_Seen_Dataset.csv` and `Test_Unseen_Dataset.csv`.
2. It loaded `Rule_Dataset.csv`, while the supplied file is named `Rules_Dataset.csv`.
3. It expected rule columns named `RuleNumber` and `Rule`; the supplied rule dataset uses `RuleName`, `RuleDescription`, `Example`, and `Template`.
4. The final execution cell called `retrieve_with_threshold`, which was not defined in the uploaded notebook. The cleaned notebook calls `retrieve_context`.
5. The original notebook saved `MetRAG_Results.csv`. The cleaned notebook uses HyRAG-specific output filenames and does not overwrite the provided paper-result CSVs.
6. The original inference function assumed every input file contains a `Category` column. `Test_Unseen_Dataset.csv` does not. The cleaned notebook handles `Category` as optional.
7. The original `match_with_priority` function contained unreachable code after its first `return`; this dead code was removed.
8. Imports that were not required by the provided pipeline were removed from the cleaned public notebook/module.

## Dataset observations

These observations are descriptive and do not modify the supplied datasets:

- `Context_Dataset.csv`: 246 rows, 245 unique values in `EventTemplate`.
- `Test_Seen_Dataset.csv`: 4,940 rows, 493 unique templates; 2,460 rows are labeled `Seen` and 2,480 are labeled `Unseen`.
- `Test_Unseen_Dataset.csv`: 6,520 rows, 652 unique templates from Mac, Thunderbird, BGL, and OpenStack.
- Source labels use inconsistent capitalization across files (for example, `Hpc` vs `HPC`, `Hdfs` vs `HDFS`, and `Openssh` vs `OPENSSH`). The package leaves these labels unchanged to preserve the uploaded data.

## Result-file provenance issue to resolve before publication

The provided result CSVs do **not** appear to have been produced by the exact uploaded notebook version:

- `HyRAG_Results_Seen_Datasets.csv` contains `Rule_Score` and `Total_Score`, while the uploaded notebook's final result dictionary records only `Similarity_Score`.
- `HyRAG_Results_Unseen_Dataset.csv` contains `Rule_Score` and includes `Context_Source = Combined` for some rows, whereas the uploaded notebook implements sequential semantic -> rule -> fallback retrieval and does not emit a `Combined` context source.
- `HyRAG_Results_Seen_Datasets.csv` contains an entirely empty `Unnamed: 3` column.
- Some predictions in the supplied seen-results file contain explanatory prose despite the prompt requesting template-only output.

Because these differences may reflect an earlier experimental implementation, the cleaned notebook intentionally follows the sequential HyRAG pipeline described in the supplied explanation rather than fabricating scoring logic that is not present in the uploaded notebook.

**Recommended release action:** before tagging the repository as the exact artifact used for the paper, identify the final code version that generated the reported result files, or regenerate the public results with the cleaned notebook and clearly label them as regenerated results.

## Licensing/data redistribution check

Before publishing, confirm that each redistributed dataset permits public redistribution in this form. If any data originate from third-party datasets with separate licenses or citation requirements, add those notices to the repository and cite the original dataset sources.
