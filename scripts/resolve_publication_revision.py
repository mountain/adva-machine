"""Resolve a recorded Git identity after the documented publication withdrawal.

This locates a commit; it grants no authority and does not waive byte, ancestry,
profile, or runtime checks. Historical receipts keep their original identities.
"""
import json
import re
from pathlib import Path


def resolve_revision(root, original):
    if not re.fullmatch(r"[0-9a-f]{40}", original):
        raise ValueError("a complete historical commit identity is required")
    record = Path(root) / "governance/withdrawals/history-map-2026-09-16.json"
    if not record.is_file():
        return original
    document = json.loads(record.read_text())
    if document.get("schema") != "adva.publication-history-correction.v0":
        raise ValueError("unrecognized publication correction record")
    mapped = document["commit_map"].get(original, original)
    if not re.fullmatch(r"[0-9a-f]{40}", mapped) or mapped == "0" * 40:
        raise ValueError("invalid mapped commit identity")
    return mapped
