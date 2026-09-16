"""The symbol-surface advance profile must carry its contract chain and live pins.

This is a regression test for a real breakage. The symbol-surface README was
edited to withhold an unearned label, and the pins binding it were not moved:
the catalogue reported InvalidCatalog and four catalogue tests failed, while the
contract pin in the advance profile broke silently because the existing test for
this module imports only `FILES`, `check_loaded` and `check_payload_bindings`
and never reaches the pin-checking path. Nothing here re-runs the profile; it
checks the bindings that a run would enforce at preflight.
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "experiments/advance_symbol_surface"
ACTIVE = DIR / "contract-v9.json"
V8 = DIR / "contract-v8.json"
V7 = DIR / "contract-v7.json"
V6 = DIR / "contract-v6.json"
V5 = DIR / "contract-v5.json"
V4 = DIR / "contract-v4.json"
V3 = DIR / "contract-v3.json"
V2 = DIR / "contract-v2.json"
V1 = DIR / "contract-v1.json"
FROZEN = DIR / "contract.json"
MODULE = ROOT / "python/adva/advance_surface.py"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_chain_supersedes_by_digest_from_v0_through_the_active_contract():
    """Each contract names the digest of the one before it, so none can be edited."""
    chain = [ACTIVE, V8, V7, V6, V5, V4, V3, V2, V1, FROZEN]
    for path in chain:
        assert path.exists(), path.name
    for newer, older in zip(chain, chain[1:]):
        contract = load(newer)
        assert contract["version"] == load(newer)["version"]
        supersedes = contract["supersedes"]
        assert supersedes["path"] == f"experiments/advance_symbol_surface/{older.name}"
        assert supersedes["sha256"] == hashlib.sha256(older.read_bytes()).hexdigest()
        assert supersedes["note"].strip()
    assert load(ACTIVE)["version"] == 9
    assert load(V8)["version"] == 8
    assert load(V7)["version"] == 7
    assert load(V6)["version"] == 6
    assert load(V5)["version"] == 5
    assert load(V4)["version"] == 4
    assert load(V3)["version"] == 3
    assert load(V2)["version"] == 2
    assert load(V1)["version"] == 1
    assert load(FROZEN)["version"] == 0


def test_the_frozen_contract_still_describes_the_first_run():
    """The frozen version keeps its original identity rather than being updated."""
    frozen = load(FROZEN)
    assert frozen["version"] == 0
    assert frozen["date"] == "2026-09-10"
    assert "supersedes" not in frozen
    assert frozen["pins"]["experiments/symbol_surface/README.md"] == (
        "e5a38e5745de316fbba026705230ee9d090221a1a0fb836c0b31b80af73eab37"
    )


def test_the_successors_only_moved_the_base_and_not_the_pins():
    """Successors v2-v9 keep the inputs; v4-v9 preserve every execution limit."""
    assert load(V2)["pins"] == load(V1)["pins"]
    assert load(V3)["pins"] == load(V2)["pins"]
    changed_metadata = {"version", "date", "base_commit", "supersedes"}
    assert {k: v for k, v in load(ACTIVE).items() if k not in changed_metadata} == {
        k: v for k, v in load(V8).items() if k not in changed_metadata
    }
    assert {k: v for k, v in load(V8).items() if k not in changed_metadata} == {
        k: v for k, v in load(V7).items() if k not in changed_metadata
    }
    assert {k: v for k, v in load(V7).items() if k not in changed_metadata} == {
        k: v for k, v in load(V6).items() if k not in changed_metadata
    }
    assert {k: v for k, v in load(V6).items() if k not in changed_metadata} == {
        k: v for k, v in load(V5).items() if k not in changed_metadata
    }
    assert {k: v for k, v in load(V5).items() if k not in changed_metadata} == {
        k: v for k, v in load(V4).items() if k not in changed_metadata
    }
    assert {k: v for k, v in load(V4).items() if k not in changed_metadata} == {
        k: v for k, v in load(V3).items() if k not in changed_metadata
    }


def test_every_pin_in_the_active_contract_matches_the_live_file():
    """This is the check whose absence let the breakage through."""
    active = load(ACTIVE)
    assert active["pins"], "the contract must pin its inputs"
    for relative, expected in active["pins"].items():
        path = ROOT / relative
        assert path.exists(), relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"{relative} changed without the pin moving"


def test_the_module_uses_the_successor_and_verifies_the_frozen_digest():
    source = MODULE.read_text(encoding="utf-8")
    assert 'CONTRACT = ROOT / "experiments/advance_symbol_surface/contract-v9.json"' in source
    # The chain check is generic: it hashes whatever the contract names, so a new
    # successor does not require editing the module.
    assert 'contract.get("version", 0) < 1 or "supersedes" not in contract' in source
    assert 'superseded = ROOT / contract["supersedes"]["path"]' in source


def test_the_base_commit_boundary_holds_at_this_commit():
    """The profile requires nothing under crates to have changed since its base."""
    active = load(ACTIVE)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "publication_revision", ROOT / "scripts/resolve_publication_revision.py")
    resolver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resolver)
    base = resolver.resolve_revision(ROOT, active["base_commit"])
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=ROOT, capture_output=True
    )
    assert ancestor.returncode == 0, "the base commit is not an ancestor of HEAD"
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--no-ext-diff", base, "--",
         "Cargo.toml", "Cargo.lock", "crates"],
        cwd=ROOT,
        capture_output=True,
    )
    assert diff.returncode == 0, (
        "the Rust boundary moved since the successor's base commit; the successor "
        "needs a new base commit rather than a relaxed check"
    )


def test_the_frozen_contract_is_expected_to_fail_on_its_edited_input():
    """Replaying the frozen contract now fails, and that is by design, not a drift.

    Asserting this keeps the divergence visible: if the README ever returned to
    the frozen bytes, this test would say so rather than let the note in the
    successor quietly become false.
    """
    frozen = load(FROZEN)
    live = hashlib.sha256(
        (ROOT / "experiments/symbol_surface/README.md").read_bytes()
    ).hexdigest()
    assert frozen["pins"]["experiments/symbol_surface/README.md"] != live
