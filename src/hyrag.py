"""Core retrieval utilities for HyRAG.

This module implements the sequential retrieval policy used by the cleaned
replication package:
  1) thresholded semantic retrieval,
  2) rule-based retrieval,
  3) top-k semantic fallback.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

RULE_PATTERNS = [
    ("url", r"\bhttps?://[^\s]+\b"),
    ("mac_eui64", r"\b(?:[0-9A-Fa-f]{2}[:-]){7}[0-9A-Fa-f]{2}\b"),
    ("mac_standard", r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    ("human_datetime", r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}(?:\s+[A-Z]{2,4})?\s+\d{4}\b"),
    ("datetime", r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b"),
    ("date", r"\b\d{4}-\d{2}-\d{2}\b"),
    ("time", r"\b\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b"),
    ("ipv4_with_port", r"/?\b(?:\d{1,3}\.){3}\d{1,3}:\d+\b"),
    ("file_path", r"(?<!https:)\/(?:[A-Za-z0-9_.-]+\/)*[A-Za-z0-9_.-]+"),
    ("domain_with_port", r"\b(?:[A-Za-z0-9-]+\.){2,}[A-Za-z]{2,}(?::\d+)\b"),
    ("ipv4", r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ("domain", r"\b(?:[A-Za-z0-9-]+\.){2,}[A-Za-z]{2,}\b"),
    ("uuid", r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    ("hexadecimal", r"\b0x[0-9A-Fa-f]+\b"),
    ("data_volume", r"\b\d+(?:\.\d+)?\s*(?:B|KB|MB|GB|TB|Bytes?|Kilobytes?|Megabytes?|Gigabytes?|Terabytes?)\b"),
    ("duration", r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|minutes?|mins?|seconds?|secs?|milliseconds?|ms)\b"),
    ("version_number", r"\b\d+(?:\.\d+){2,}\b"),
    ("decimal", r"(?<![\d.])\b\d+\.\d+\b(?![\d.])"),
    ("key_value_pair", r"\b[A-Za-z_][A-Za-z0-9_]*\s*[:=]\s*[^\s]+"),
    ("alphanumeric_id", r"\b(?=[A-Za-z0-9_.+-]*[A-Za-z])(?=[A-Za-z0-9_.+-]*\d)[A-Za-z0-9_.+-]+\b"),
    ("numeric_id", r"(?<![\w.:/-])\d+(?![\w.:/-])"),
]
STATIC_PATTERN = r"[A-Za-z]+(?:\s+[A-Za-z]+)*"


def match_with_priority(text: str) -> Dict[str, Dict[str, object]]:
    """Match non-overlapping dynamic patterns in priority order."""
    matched_spans: List[Tuple[int, int]] = []
    results = {name: [] for name, _ in RULE_PATTERNS}
    results["static_message"] = []

    def overlaps(start: int, end: int) -> bool:
        return any(start < old_end and end > old_start for old_start, old_end in matched_spans)

    dynamic_found = False
    for rule_name, pattern in RULE_PATTERNS:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if not overlaps(start, end):
                matched_spans.append((start, end))
                results[rule_name].append(match.group())
                dynamic_found = True

    if not dynamic_found:
        results["static_message"] = [m.group() for m in re.finditer(STATIC_PATTERN, text)]

    return {
        name: {"match": "yes" if matches else "no", "patterns": matches}
        for name, matches in results.items()
    }


def build_rules_dict(rules_df):
    """Build lookup dictionary from the public Rules_Dataset.csv schema."""
    return {
        row["RuleName"]: {
            "description": row["RuleDescription"],
            "example": row["Example"],
            "template": row["Template"],
        }
        for _, row in rules_df.iterrows()
    }


def similarity_retrieval(query, embeddings, vectorstore, threshold=0.7, k=3):
    """Return threshold-qualified semantic context and the mean similarity."""
    query_embedding = embeddings.embed_query(query)
    docs = vectorstore.similarity_search_by_vector(query_embedding, k=k)
    kept, scores = [], []
    for doc in docs:
        doc_embedding = embeddings.embed_query(doc.page_content)
        score = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        if score >= threshold:
            kept.append(doc.page_content)
            scores.append(float(score))
    return "\n".join(kept), (float(np.mean(scores)) if scores else 0.0), bool(kept)


def rule_based_retrieval(query, rules_dict, top_k=3):
    """Return up to top_k rule examples in pattern-priority order."""
    matches = match_with_priority(query)
    examples = []
    matched_rules = []
    for rule_name, info in matches.items():
        if info["match"] == "yes" and rule_name in rules_dict:
            matched_rules.append(rule_name)
            examples.append(
                f"Example: {rules_dict[rule_name]['example']}\n"
                f"Template: {rules_dict[rule_name]['template']}"
            )
    examples = examples[:top_k]
    matched_rules = matched_rules[:top_k]
    return "\n\n".join(examples), matched_rules


def retrieve_context(query, embeddings, vectorstore, rules_dict, k=3, threshold=0.7):
    """Sequential HyRAG retrieval: semantic -> rule -> semantic fallback."""
    semantic_context, semantic_score, found = similarity_retrieval(
        query, embeddings, vectorstore, threshold=threshold, k=k
    )
    if found:
        return semantic_context, {
            "context_source": "Similarity-Based",
            "similarity_score": semantic_score,
            "matched_rules": [],
        }

    rule_context, matched_rules = rule_based_retrieval(query, rules_dict, top_k=k)
    if rule_context:
        return rule_context, {
            "context_source": "Rule-Based",
            "similarity_score": semantic_score,
            "matched_rules": matched_rules,
        }

    fallback_context, _, _ = similarity_retrieval(
        query, embeddings, vectorstore, threshold=0.0, k=k
    )
    return fallback_context, {
        "context_source": "Fallback-TopK",
        "similarity_score": semantic_score,
        "matched_rules": [],
    }
