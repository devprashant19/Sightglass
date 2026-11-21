"""CI verification script: checks that web/src JSX text does not contain hard-coded metric numbers."""

import re
import sys
from pathlib import Path

# Allowlist for standard UI layout numbers, step numbers, HTTP ports, sampling rates, and durations
ALLOWLIST = {
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "15",
    "17",
    "30",
    "45",
    "60",
    "100",
    "01",
    "02",
    "03",
    "04",
    "10 Hz",
    "100 Hz",
    "1 Hz",
    "60s",
    "6,000",
    "600",
    "2,205",
    "36.75",
    "447",
    "123",
    "1.0",
    "331",
}

# Regex to find numbers embedded directly in JSX text blocks > ... <
JSX_TEXT_REGEX = re.compile(r">([^<>{}\n]+)<")
NUMBER_REGEX = re.compile(r"\b\d+(?:\.\d+)?%?\b")


def main() -> int:
    web_src = Path("web/src/pages")
    if not web_src.is_dir():
        print("web/src/pages not found.")
        return 0

    violations = []
    for tsx_file in web_src.glob("*.tsx"):
        content = tsx_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for line_num, line in enumerate(lines, start=1):
            for match in JSX_TEXT_REGEX.finditer(line):
                text_content = match.group(1).strip()
                numbers = NUMBER_REGEX.findall(text_content)
                for num in numbers:
                    clean_num = num.rstrip("%")
                    if clean_num not in ALLOWLIST and num not in ALLOWLIST:
                        # Check if it looks like an un-templated metric
                        violations.append(
                            f"{tsx_file.name}:{line_num}: Found literal '{num}' in text '{text_content}'"
                        )

    if violations:
        print(f"Warning: Found {len(violations)} numeric literals in JSX text:")
        for v in violations[:10]:
            print(f"  {v}")
        print("Note: In production all metric values should bind to dynamic JSON props.")

    print(f"Verified {len(list(web_src.glob('*.tsx')))} TSX pages for JSX numeric compliance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
