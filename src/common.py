"""Stable project paths and evidence helpers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_json(path):
    return json.loads((ROOT / path).read_text())

def write_json(path, value):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
