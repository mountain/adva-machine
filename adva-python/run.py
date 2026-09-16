#!/usr/bin/env python3
"""Python research execution with Rust admission and trace receiving."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolchain.cli import main

raise SystemExit(main(["run", *sys.argv[1:], "--engine", "python"]))
