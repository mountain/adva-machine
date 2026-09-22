"""Terminology homes must parse, must declare their boundaries, and must point at real files.

The five files in docs/terminology do not share one term schema, and that is
allowed: they were written at different times for different subjects. What is not
allowed is a home that parses but points nowhere, a term that silently drops the
boundary list it was supposed to carry, or an authority block that grants more than
"proposed". This checks only those, so it passes on the older shapes and still
catches the failure this repository has already made once: a path in a pointer that
was never resolved.
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
TERMS = ROOT / "docs/terminology"
COMMON = ("name", "status", "effect", "input", "output")
PATH_KEYS = ("related_homes", "report", "origin", "evidence", "contract")


def files():
    return sorted(TERMS.glob("*.json"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_home_parses_and_is_proposed():
    assert files(), "no terminology files at all"
    for path in files():
        doc = load(path)
        assert doc.get("status") == "Proposed", path.name
        # Version 1 is admitted as well as version 0, by the direction on
        # 2026-09-22. The two commit-state reconcile revisions were brought to
        # one in-file version, and their distinction is carried by the file name
        # and the predecessor field instead. This check exists so that a home
        # grants no more than "proposed"; it was never a claim that a document
        # revision number must be zero or absent.
        assert doc.get("version") in (0, 1) or "version" not in doc, path.name


def test_every_term_carries_the_common_core_and_any_boundary_it_declares():
    for path in files():
        doc = load(path)
        for term in doc.get("terms") or []:
            for key in COMMON:
                assert key in term, "%s: %s lacks %s" % (path.name, term.get("name"), key)
                value = term[key]
                if isinstance(value, (list, str)):
                    assert value, "%s: %s has an empty %s" % (path.name, term.get("name"), key)
            for key in ("does_not_imply", "refusal", "residual", "preserves", "preconditions"):
                if key in term:
                    assert term[key], "%s: %s declares an empty %s" % (
                        path.name, term.get("name"), key)


def test_no_home_grants_more_than_proposed():
    for path in files():
        doc = load(path)
        authority = doc.get("authority")
        if authority is None:
            continue
        assert authority.get("native_admission") == "NotGranted", path.name
        assert authority.get("stable_keywords_added", []) == [], path.name
        for key in ("semantic_identity_allocation", "numeric_acceptance_authority",
                    "diagram_admission", "library_admission"):
            if key in authority:
                assert authority[key] is False, "%s: %s" % (path.name, key)


def repo_paths(doc):
    """Every repo-relative path this home claims, wherever it is written."""
    found = []
    for entry in doc.get("related_homes") or []:
        found.append(entry["home"])
    for key in ("report", "evidence", "contract"):
        value = doc.get(key)
        if isinstance(value, str):
            found.append(value)
        elif isinstance(value, dict) and isinstance(value.get("path"), str):
            found.append(value["path"])
    origin = doc.get("origin") or {}
    source = origin.get("source_document")
    if isinstance(source, dict) and isinstance(source.get("path"), str):
        found.append(source["path"])
    return [p for p in found if not p.startswith(("http://", "https://"))]


def test_every_claimed_path_exists():
    missing = []
    for path in files():
        doc = load(path)
        for relative in repo_paths(doc):
            if not (ROOT / relative).exists():
                missing.append("%s -> %s" % (path.name, relative))
    assert not missing, "terminology homes pointing at nothing: %s" % missing


def test_registered_marks_are_unique_and_their_overloads_are_declared():
    """A mark registered twice in one home is a mistake; an overload must be declared."""
    for path in files():
        doc = load(path)
        marks = [t["notation"] for t in doc.get("terms") or [] if t.get("notation")]
        assert len(marks) == len(set(marks)), "%s registers a mark twice" % path.name
        glyphs = set()
        for mark in marks:
            glyphs |= set(re.findall(r"\[\]|\(\)|<>|\[< >\]|\(> <\)", mark))
        declared = []
        for entry in doc.get("overload_declarations") or []:
            declared.extend(entry.get("marks", []))
        for glyph in declared:
            assert glyph in glyphs, "%s declares an overload for %s but does not register it" % (
                path.name, glyph)
        if glyphs and any(g in ("[]", "()", "<>") for g in glyphs):
            assert doc.get("overload_declarations"), (
                "%s registers bracket glyphs without declaring their other homes" % path.name)
