from pathlib import Path
files = [
"backend/app/main.py",
"backend/requirements.txt",
"extension/manifest.json",
"extension/popup.js",
"docs/formulario_prueba.html",
]
for f in files:
    b = Path(f).read_bytes()
    print(f, "LF:", b.count(b"\n"), "CR:", b.count(b"\r"), "SIZE:", len(b))
