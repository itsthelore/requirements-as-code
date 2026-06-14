"""Make the package root importable for `providers`, `scenarios`, `scoring`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
