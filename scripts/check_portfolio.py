"""Run portable financial checks and all distributed checksum checks."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
for project in sorted(ROOT.iterdir()):
    if not project.is_dir() or not (project/'data').is_dir():continue
    for folder in ('src','tests','data','reports'):
        if not (project/folder).is_dir():raise SystemExit(f'Missing {project.name}/{folder}')
    verifier=project/'src/verify_package.py'
    if verifier.exists():subprocess.run([sys.executable,str(verifier)],check=True)
for project in ['kspi-valuation-bank-risk','unilever-equity-valuation','consumer-lending-credit-risk']:
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT/project,check=True)
subprocess.run([sys.executable,'src/verify_workbook.py'],cwd=ROOT/'kspi-valuation-bank-risk',check=True)
subprocess.run([sys.executable,'src/analyse.py','--verify-reference'],cwd=ROOT/'kspi-valuation-bank-risk',check=True)
print('PASS: portable financial checks and project structure. See individual READMEs for numerical analyses.')
