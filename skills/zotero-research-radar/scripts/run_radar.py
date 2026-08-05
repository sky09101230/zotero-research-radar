"""Run the repository's JSON CLI from a Codex skill invocation."""

from __future__ import annotations

import subprocess
import sys


if __name__ == "__main__":
    raise SystemExit(subprocess.call(["uv", "run", "radar", *sys.argv[1:]]))
