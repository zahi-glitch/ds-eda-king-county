"""Runs the whole project, in order:  clean data -> numbers report -> pictures -> PDF.

    python src/run_all.py          # everything
    python src/run_all.py --no-pdf # skip LaTeX

You can also run each step yourself (see README.md).
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = ["src/01_clean_data.py", "src/02_make_report.py", "src/03_make_images.py"]

for step in STEPS:
    print(f"\n=== {step}")
    if subprocess.run([sys.executable, step], cwd=ROOT).returncode:
        sys.exit(f"stopped: {step} failed")

if "--no-pdf" not in sys.argv:
    print("\n=== slides -> output/King_County_talk.pdf (with pauses) and King_County_talk_no_pauses.pdf")
    for tex, name in [("main", "King_County_talk"), ("main_nopauses", "King_County_talk_no_pauses")]:
        if shutil.which("latexmk"):
            subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", tex + ".tex"], cwd=ROOT / "slides", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif shutil.which("pdflatex"):
            for _ in range(2):
                subprocess.run(["pdflatex", "-interaction=nonstopmode", tex + ".tex"], cwd=ROOT / "slides", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            sys.exit("No LaTeX found. Install TeX Live / MacTeX / MiKTeX, or use --no-pdf.")
        pdf = ROOT / "slides" / (tex + ".pdf")
        (ROOT / "output").mkdir(exist_ok=True)
        if pdf.exists():
            shutil.copy(pdf, ROOT / "output" / (name + ".pdf"))
            print(f"[saved] output/{name}.pdf")
        else:
            sys.exit(f"LaTeX failed: see slides/{tex}.log")
