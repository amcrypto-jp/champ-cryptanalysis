#!/usr/bin/env python3
"""Regenerate REPORT.tex, REPORT.pdf and offline REPORT.html with Pandoc/Tectonic."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import shutil

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--pandoc", default="pandoc")
parser.add_argument("--tectonic", default="tectonic")
args = parser.parse_args()

common = [args.pandoc, "REPORT.md", "--standalone",
          "--from=markdown+tex_math_single_backslash", "--shift-heading-level-by=-1",
          "--lua-filter=assets/layout.lua"]
subprocess.run(common + ["--to=html5", "--mathml", "--embed-resources",
                        "--css=assets/report.css", "--output=REPORT.html"],
               cwd=root, check=True)
subprocess.run(common + ["--to=latex", "--output=REPORT.tex", "--pdf-engine=tectonic",
                        "--include-in-header=assets/preamble.tex",
                        "--variable=papersize:a4", "--variable=fontsize:11pt",
                        "--variable=geometry:margin=23mm",
                        "--variable=mainfont:DejaVu Serif",
                        "--variable=sansfont:DejaVu Sans",
                        "--variable=monofont:DejaVu Sans Mono",
                        "--variable=monofontoptions:Scale=0.82"],
               cwd=root, check=True)
with tempfile.TemporaryDirectory(prefix="champ-report-build-") as tmp:
    subprocess.run([args.tectonic, "--outdir", tmp, str(root / "REPORT.tex")],
                   cwd=root, check=True)
    shutil.copyfile(Path(tmp) / "REPORT.pdf", root / "REPORT.pdf")
print("Built REPORT.html, REPORT.tex and REPORT.pdf")
