import os
import json
from pathlib import Path

def test_file_lf_counts():
    files_to_check = {
        "backend/app/main.py": 40,
        "backend/requirements.txt": 6,
        "extension/manifest.json": 25,
        "extension/popup.js": 150,
        "docs/formulario_prueba.html": 80
    }
    
    root_dir = Path(__file__).parent.parent.parent
    
    for relative_path, min_lf in files_to_check.items():
        filepath = root_dir / relative_path
        assert filepath.exists(), f"File not found: {relative_path}"
        content = filepath.read_bytes()
        lf_count = content.count(b"\n")
        assert lf_count >= min_lf, f"{relative_path} has {lf_count} LFs, expected at least {min_lf}"

def test_manifest_is_valid_json():
    root_dir = Path(__file__).parent.parent.parent
    manifest_path = root_dir / "extension" / "manifest.json"
    assert manifest_path.exists(), "manifest.json not found"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "manifest_version" in data
    assert data["manifest_version"] == 3

def test_requirements_format():
    root_dir = Path(__file__).parent.parent.parent
    req_path = root_dir / "backend" / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found"
    
    lines = req_path.read_text(encoding="utf-8").splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    assert len(non_empty_lines) >= 7, "requirements.txt has too few dependencies"
    
    for line in non_empty_lines:
        assert " " not in line.strip(), f"Invalid line in requirements.txt: '{line}'"
