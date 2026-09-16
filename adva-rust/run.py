#!/usr/bin/env python3
"""Rust toolchain entry over the common request format."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolchain.cli import main

raise SystemExit(main(["run", *sys.argv[1:], "--engine", "rust"]))
