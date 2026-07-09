import sys
from pathlib import Path

# Ensure the project root (containing the w2e package) is importable when pytest
# runs from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
