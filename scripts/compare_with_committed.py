"""Check that a fresh clone regenerates the committed results exactly.

Run from the root of a fresh clone, after the pipeline (see TESTING.md):

  python scripts/compare_with_committed.py results   # headline numbers in results/summary.json
  python scripts/compare_with_committed.py export    # every file in web/public/data

A file counts only if the pipeline rewrote it after the clone was made, so an untouched
committed copy can never pass as "reproduced". Generation time and git SHA are ignored.
Exit 1 if anything differs or was not regenerated.
"""

import json
import subprocess
import sys
from pathlib import Path

VOLATILE = {"generated_at", "git_sha", "seconds", "latency_ms", "uptime_s"}


def committed(path: str):
    out = subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=True)
    return json.loads(out.stdout.decode("utf-8"))


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in VOLATILE}
    if isinstance(x, list):
        return [strip(v) for v in x]
    if isinstance(x, float):
        return round(x, 9)
    return x


def fresh(path: str) -> bool:
    """True only if the file was written after this clone was made, i.e. the pipeline regenerated it."""
    return Path(path).stat().st_mtime > Path(".git/index").stat().st_mtime + 1


def results() -> int:
    if not fresh("results/summary.json"):
        print("NOT REGENERATED: results/summary.json is still the committed copy")
        return 1
    new, old = (
        json.loads(Path("results/summary.json").read_text(encoding="utf-8")),
        committed("results/summary.json"),
    )
    checks = [
        ("engine mean macro-F1", ["engine", "mean_macro_f1"]),
        ("engine joint exact match", ["engine", "joint_exact_match"]),
        ("engine claim accuracy", ["engine", "claim_accuracy"]),
        ("engine consistency", ["engine", "consistency_pct"]),
        ("checker round trip", ["checker", "roundtrip_pct"]),
        ("checker corruption caught", ["checker", "corruption_caught_pct"]),
        ("test cycles", ["dataset", "test"]),
    ]
    same = 0
    for name, path in checks:
        a, b = new, old
        for k in path:
            a, b = a[k], b[k]
        ok = round(a, 9) == round(b, 9)
        same += ok
        print(f"{'SAME' if ok else 'DIFF'}  {name}: regenerated {a} vs committed {b}")
    nb = {b["id"]: b for b in new["baselines"]}
    for b in old["baselines"]:
        if b.get("status") != "done":
            continue
        a = nb.get(b["id"], {}).get("mean_macro_f1")
        ok = a is not None and abs(a - b["mean_macro_f1"]) < 1e-9
        same += ok
        checks.append((b["id"], None))
        print(
            f"{'SAME' if ok else 'DIFF'}  baseline {b['id']}: regenerated {a} vs committed {b['mean_macro_f1']}"
        )
    print(f"REPRODUCED {same}/{len(checks)} headline numbers")
    return 0 if same == len(checks) else 1


def export() -> int:
    files = subprocess.run(
        ["git", "ls-files", "web/public/data"], capture_output=True, text=True, check=True
    ).stdout.split()
    same, diffs = 0, []
    for f in files:
        p = Path(f)
        if not p.is_file():
            diffs.append(f"missing {f}")
            continue
        if not fresh(f):
            diffs.append(f"not regenerated {f}")
            continue
        if strip(json.loads(p.read_text(encoding="utf-8"))) == strip(committed(f)):
            same += 1
        else:
            diffs.append(f)
    for d in diffs[:10]:
        print("DIFF", d)
    print(f"EXPORT IDENTICAL {same}/{len(files)} files")
    return 0 if same == len(files) else 1


if __name__ == "__main__":
    sys.exit(results() if sys.argv[1] == "results" else export())
