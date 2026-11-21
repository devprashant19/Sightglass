"""The dashboard gate must catch hand-typed result numbers, and must not flag layout counts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_no_hardcoded_numbers import violations_in  # noqa: E402


def test_catches_planted_metrics(tmp_path: Path) -> None:
    f = tmp_path / "Planted.tsx"
    f.write_text(
        "const A = () => <p>Mean macro-F1 0.942 and 98.4% verified</p>;\n"
        "const T = [{ t: 'Fast', p: 'Scores 0.97 on the cooler' }];\n",
        encoding="utf-8",
    )
    found = violations_in(f)
    assert len(found) == 3
    assert any("'0.942'" in v for v in found)
    assert any("'98.4%'" in v for v in found)
    assert any("'0.97'" in v for v in found)


def test_allows_small_counts_and_method_constants(tmp_path: Path) -> None:
    f = tmp_path / "Fine.tsx"
    f.write_text(
        "const A = () => <p>Four parts, 4 sensors groups, UCI #447, numbers changed by 20%</p>;\n"
        "// a comment with 0.99 is ignored\n",
        encoding="utf-8",
    )
    assert violations_in(f) == []


def test_the_real_dashboard_passes() -> None:
    root = Path(__file__).resolve().parents[1] / "web" / "src"
    files = [p for p in root.rglob("*.tsx") if "test" not in p.parts]
    assert files, "read nothing: the gate would pass an empty folder"
    assert [v for p in files for v in violations_in(p)] == []
