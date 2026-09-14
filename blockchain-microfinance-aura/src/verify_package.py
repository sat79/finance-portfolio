"""Check the distributed baseline before regenerating or editing outputs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    manifest=json.loads((ROOT/'SHA256SUMS.json').read_text());errors=[]
    for name,expected in manifest.items():
        path=ROOT/name
        if not path.is_file():errors.append(f'Missing: {name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected:errors.append(f'Changed: {name}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(manifest)} distributed files match the baseline. Checksums are not proof of authenticity.')
if __name__=='__main__':main()
