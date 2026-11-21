"""CI check: the dashboard must not hard-code result numbers in visible text.

Every metric on the site is read from the exported JSON. This scans the JSX text and the
static copy strings in web/src for numbers that look like results (decimals, percentages,
or multi-digit figures) and fails if any is not on the short allow-list of method constants.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Method constants and identifiers that are not results.
ALLOWED = {
    "447",  # UCI dataset id
    "20%",  # size of the corruption used to test the checker (configs, phase 05)
    "1σ",
    "404",
}
# Small integers are layout, ordinals or counts of fixed things (four parts, three failure modes).
SMALL_INT = re.compile(r"^\d$")

JSX_TEXT = re.compile(r">([^<>{}]+)<")
COPY_STRING = re.compile(r"(?:\b[pt]|text|title|note|label|sub):\s*'([^']*)'")
NUMBER = re.compile(r"(?<![\w#.])\d+(?:[.,]\d+)*(?:\s?%|σ)?")


def violations_in(path: Path) -> list[str]:
    out: list[str] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith(("//", "*", "/*", "import ")):
            continue
        texts = [m.group(1) for m in JSX_TEXT.finditer(line)] + [
            m.group(1) for m in COPY_STRING.finditer(line)
        ]
        for text in texts:
            for m in NUMBER.finditer(text):
                num = m.group(0).replace(" ", "")
                if SMALL_INT.match(num) or num in ALLOWED:
                    continue
                out.append(f"{path.as_posix()}:{n}: '{num}' in \"{text.strip()[:80]}\"")
    return out


def main() -> int:
    root = Path("web/src")
    if not root.is_dir():
        print("web/src not found", file=sys.stderr)
        return 1
    files = [p for p in root.rglob("*.tsx") if "test" not in p.parts] + [root / "lib" / "data.ts"]
    found = [v for f in files if f.is_file() for v in violations_in(f)]
    if found:
        print(
            f"Found {len(found)} hard-coded numbers in dashboard text (load them from the export instead):"
        )
        for v in found:
            print(f"  {v}")
        return 1
    print(f"OK: {len(files)} files, no hard-coded result numbers in visible text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
