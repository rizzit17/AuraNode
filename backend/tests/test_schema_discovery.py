import os
import sys
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.schema_discovery import canonicalize_label, discover_schema

def test_canonicalize_label():
    assert canonicalize_label("acquired") == "ACQUIRED"
    assert canonicalize_label("bought out") == "ACQUIRED"
    assert canonicalize_label("purchased") == "ACQUIRED"
    assert canonicalize_label("invested in") == "INVESTED_IN"
    assert canonicalize_label("merged with") == "MERGED_WITH"

def test_schema_metrics_format():
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ingestion", "sample_data"))
    metrics_path = os.path.join(sample_dir, "schema_metrics.json")
    assert os.path.exists(metrics_path), "schema_metrics.json should be present"
    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "raw_relation_labels_count" in data
    assert "canonical_relations_count" in data
    assert "schema_reduction_percentage" in data
