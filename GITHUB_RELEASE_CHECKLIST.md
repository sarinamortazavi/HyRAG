# GitHub Release Checklist

Before publishing the repository:

- [ ] Confirm the final paper title exactly matches the README.
- [ ] Fill in `CITATION.cff.template` and rename it to `CITATION.cff`.
- [ ] Add the final author-approved software/data license.
- [ ] Confirm third-party dataset redistribution and citation requirements.
- [ ] Resolve the result-file provenance differences described in `REPLICATION_NOTES.md`.
- [ ] Run `Scripts/HyRAG_Framework.ipynb` from a clean environment.
- [ ] Record the exact Python/CUDA/PyTorch/package versions used for the final reproducibility run.
- [ ] Check that no API keys, Hugging Face tokens, local paths, or private data are present.
- [ ] Add the paper DOI/URL when available.
- [ ] Create a GitHub release/tag (for example `v1.0.0`) corresponding to the camera-ready artifact.
