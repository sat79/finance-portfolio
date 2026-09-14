"""Check distributed file hashes for accidental corruption or modification."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError("Unsafe path in checksum manifest")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Changed or corrupt file: {relative}")
        count += 1
    print(f"PASS: {count} distributed files match the checksum manifest.")
    print("Checksums detect accidental changes; they are not proof of authorship or authenticity.")


if __name__ == "__main__":
    main()
