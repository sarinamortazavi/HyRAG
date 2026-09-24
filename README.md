# HyRAG: A Hybrid Retrieval-Augmented Framework for Enhancing Compact LLMs in Log Parsing

This repository contains the replication package for our paper **"HyRAG: A Hybrid Retrieval-Augmented Framework for Enhancing Compact LLMs in Log Parsing."**


## Authors

- **Sarina Mortazavi**
- **Maryam Mehrabi**
- **Moataz Chouchen**
- **Abdelwahab Hamou-Lhadj**

HyRAG is a hybrid retrieval-augmented generation framework for log template extraction with compact large language models. For each incoming log message, HyRAG first attempts semantic retrieval from a context knowledge base. If no sufficiently similar example is found, it uses rule-based retrieval over common structural patterns. If neither strategy yields context, it falls back to the top-k semantic matches.

## Repository structure

```text
HyRAG/
├── Datasets/
│   ├── Context_Dataset.csv
│   ├── Rules_Dataset.csv
│   ├── Test_Seen_Dataset.csv
│   └── Test_Unseen_Dataset.csv
├── Results/
│   ├── HyRAG_Results_Seen_Datasets.csv
│   └── HyRAG_Results_Unseen_Dataset.csv
├── Scripts/
│   └── HyRAG_Framework.ipynb
├── src/
│   └── hyrag.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Datasets

The `Datasets/` directory contains the data used to construct the HyRAG knowledge bases and evaluate the framework.

### `Context_Dataset.csv`
Semantic knowledge base containing representative log-template pairs used for embedding-based retrieval.

Columns:
- `Content`: raw log message.
- `EventId`: template/event identifier.
- `EventTemplate`: ground-truth log template.
- `Source`: source dataset.

The provided file contains **246 rows** and **245 unique templates**.

### `Rules_Dataset.csv`
Structural knowledge base containing representative examples associated with predefined rule types for common dynamic patterns such as URLs, MAC addresses, timestamps, IP addresses, ports, file paths, UUIDs, hexadecimal values, key-value pairs, and numeric identifiers.

Columns:
- `RuleName`: identifier used by the rule matcher.
- `RuleDescription`: human-readable description of the pattern.
- `Example`: representative log example.
- `Template`: corresponding log template.

### `Test_Seen_Dataset.csv`
Evaluation data drawn from datasets represented in the semantic knowledge base. The `Category` column distinguishes templates categorized as `Seen` and `Unseen` within those datasets.

The provided file contains **4,940 log messages** and **493 unique templates**.

### `Test_Unseen_Dataset.csv`
Evaluation data from source datasets not represented in the semantic knowledge base. It contains logs from BGL, Mac, OpenStack, and Thunderbird.

The provided file contains **6,520 log messages** and **652 unique templates**.

## Results

The `Results/` directory contains the provided experimental outputs.

### `HyRAG_Results_Seen_Datasets.csv`
HyRAG outputs for `Test_Seen_Dataset.csv`, including predicted templates, retrieval source, and retrieval scores recorded by the experimental code used for that run.

### `HyRAG_Results_Unseen_Dataset.csv`
HyRAG outputs for `Test_Unseen_Dataset.csv`, including predicted templates, retrieval source, and retrieval scores recorded by the experimental code used for that run.

## HyRAG retrieval pipeline

For an input log message, the public implementation follows this sequence:

1. **Semantic retrieval**
   - Embed the input log using `sentence-transformers/all-MiniLM-L6-v2`.
   - Retrieve the top `k = 3` candidate context examples.
   - Retain candidates whose cosine similarity is at least `0.7`.
   - If at least one candidate passes the threshold, use the semantic examples as context.

2. **Rule-based retrieval**
   - If semantic retrieval returns no qualifying example, evaluate the predefined regular-expression rules.
   - Retrieve up to three representative rule examples from `Rules_Dataset.csv`.

3. **Semantic fallback**
   - If neither thresholded semantic retrieval nor rule retrieval returns context, use the top three semantic matches without applying the similarity threshold.

4. **Template generation**
   - The retrieved examples and input log are inserted into the prompt.
   - The compact LLM generates a log template by replacing dynamic values with `<*>`.

## Model configuration

The supplied implementation uses:

- **Generator:** `unsloth/mistral-7b-instruct-v0.3-bnb-4bit`
- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector store:** Chroma
- **Similarity threshold:** `0.7`
- **Top-k retrieval:** `3`
- **Maximum generated tokens:** `64`

A CUDA-capable GPU is recommended for generation with the 7B model.

## Installation

Clone the repository and create a virtual environment:

```bash
git clone <YOUR_REPOSITORY_URL>
cd HyRAG
python -m venv .venv
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

For GPU execution, install the PyTorch build appropriate for your CUDA environment before running the notebook. Unsloth/bitsandbytes compatibility can depend on the CUDA and PyTorch versions available on the machine.

## Running the notebook

1. Open `Scripts/HyRAG_Framework.ipynb` from the repository root.
2. Set `DATASET_TO_RUN` to either:
   - `"seen"` for `Test_Seen_Dataset.csv`, or
   - `"unseen"` for `Test_Unseen_Dataset.csv`.
3. Run the notebook cells in order.
4. The generated output is written to the `Results/` directory with a separate filename so the provided paper results are not overwritten accidentally.

The notebook uses repository-relative paths, so no Google Drive or machine-specific paths are required.

## Python module

The reusable retrieval logic is also available in `src/hyrag.py`. This makes it easier to import and test the framework outside Jupyter.

Example:

```python
from src.hyrag import RULE_PATTERNS, match_with_priority

matches = match_with_priority("Connection from 192.168.0.10:8080 failed")
print(matches)
```

## Reproducibility notes

Please read [`REPLICATION_NOTES.md`](REPLICATION_NOTES.md) before making the repository public. It records several inconsistencies found in the original uploaded notebook/results package and explains what was corrected in the cleaned notebook.

## Citation


If you use HyRAG or this replication package in your research, please cite our paper:

S. Mortazavi, M. Mehrabi, M. Chouchen, and A. Hamou-Lhadj,  
"HyRAG: A Hybrid Retrieval-Augmented Framework for Enhancing Compact LLMs in Log Parsing,"  
CASCON 2026.


## Contact

For questions about the replication package, please open an issue in this repository or use the contact information provided in the associated paper.
