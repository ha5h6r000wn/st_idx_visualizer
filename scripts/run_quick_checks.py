#!/usr/bin/env python

import pathlib
import subprocess
import sys


def main() -> int:
    project_root = pathlib.Path(__file__).resolve().parents[1]
    cmd = [sys.executable, "-m", "pytest", "-m", "style_prep", "-vv", "tests"]
    return subprocess.call(cmd, cwd=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
