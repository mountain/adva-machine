"""Regression of an external algebraic certificate; no native proof admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
One bounded replay, one source-byte mutation, and retained-evidence integrity.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "pascal_commutator_certificate"
EVIDENCE = EXPERIMENT / "evidence"
SOURCES_PRESENT = all((ROOT / "adva-library" / name).is_file()
                      for name in ("pascal-task.adva", "pascal-witness.adva"))

# The declared per-child address-space limit is Linux-only: on a platform that
# cannot install it a bounded child dies inside preexec_fn, so these checks are
# reported as not runnable here rather than failing (Research 0210, 0213).
ADDRESS_SPACE_LIMIT_INSTALLABLE = sys.platform == "linux"
SKIP_LIMIT = ("the declared per-child address-space limit is Linux-only "
              "(Research 0210); run it on the Linux guest: docs/maintenance/LINUX_HOST_FIXTURE.md")



class PascalCommutatorCertificateTests(unittest.TestCase):
    def test_retained_evidence_is_bound_to_code_and_claim(self):
        """At least one retained execution record must bind to the current code.

        A record names the launcher digests it ran with, so a corrected launcher
        is retained as a new record rather than by editing an earlier one.
        """
        records = sorted(EVIDENCE.glob("execution*.json"))
        self.assertTrue(records, "no retained execution record")
        bound = []
        for path in records:
            report = json.loads(path.read_bytes())
            self.assertEqual(report["status"], "VerifiedExternalConditionalCertificate")
            code_ok = all(
                hashlib.sha256((EXPERIMENT / name).read_bytes()).hexdigest() == expected
                for name, expected in report["file_sha256"].items()
            )
            outputs_ok = all(
                hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == expected
                for name, expected in report["output_sha256"].items()
            )
            if code_ok and outputs_ok:
                bound.append(path.name)
        self.assertTrue(bound, f"no retained execution record binds to the current code: {[p.name for p in records]}")
        claims = tomllib.loads((ROOT / "docs" / "claims.toml").read_text())["claim"]
        matches = [c for c in claims if c["claim_id"] ==
                   "adva.bounded-verified.external-pascal-commutator-certificate.v0"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["status"], "bounded-verified")

    @unittest.skipUnless(os.name == "posix" and SOURCES_PRESENT and ADDRESS_SPACE_LIMIT_INSTALLABLE,
                         "requires the Linux-only address-space limit and the pinned adva-library submodule")
    def test_bounded_replay_preserves_and_reproduces_frozen_outputs(self):
        before = {p.name: p.read_bytes() for p in EVIDENCE.iterdir() if p.is_file()}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "fresh"
            run = subprocess.run([sys.executable, str(EXPERIMENT / "run.py"), str(output)],
                                 capture_output=True, text=True, timeout=125, check=False)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            for name in ("certificate.json", "check.json", "controls.json"):
                self.assertEqual((output / name).read_bytes(), before[name])
        self.assertEqual(before, {p.name: p.read_bytes() for p in EVIDENCE.iterdir() if p.is_file()})

    @unittest.skipUnless(SOURCES_PRESENT, "requires the pinned adva-library submodule")
    def test_actual_source_mutation_is_rejected_before_equation_checks(self):
        spec = importlib.util.spec_from_file_location("external_pascal_checker", EXPERIMENT / "check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        certificate = json.loads((EVIDENCE / "certificate.json").read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "adva-library").mkdir()
            for name in checker.PINS:
                shutil.copyfile(ROOT / "adva-library" / name, root / "adva-library" / name)
            path = root / "adva-library" / "pascal-task.adva"
            path.write_bytes(path.read_bytes() + b"\n")
            checker.ROOT = root
            with self.assertRaisesRegex(ValueError, "source bytes changed"):
                checker.verify(certificate)


if __name__ == "__main__":
    unittest.main()
