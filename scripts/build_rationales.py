"""Build reference rationales (true labels) for every real cycle, QA pairs, and validate the checker.

Outputs
  data/reference/hydraulic_healthy.json   per-component healthy reference (train split only)
  data/rationales/hydraulic.jsonl         one joint rationale per cycle, with structured claims
  data/qa/hydraulic.jsonl                 question-answer pairs (split from the real build)
  results/checker_validation.json         round-trip and corruption tests of the checker
  docs/rationale-spotcheck.md             50 random train rationales for a human read-through
"""

import json
import re
from pathlib import Path

import numpy as np

from sightglass.data.loader import load_cycles, load_splits
from sightglass.engine import fit_reference, load_links
from sightglass.eval.faithfulness import FaithfulnessConfig, parse_claims, verify
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import build_joint_rationale
from sightglass.rationales.format import format_number
from sightglass.rationales.qa import generate_cycle_qa
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha

logger = get_logger("build_rationales")


def main() -> None:
    links = load_links()
    ex = HydraulicExtractor()
    cfg = FaithfulnessConfig.load()

    train = load_cycles("hydraulic", split="train")
    ref = fit_reference(train, [ex.extract(c) for c in train], links)
    ref_path = Path("data/reference/hydraulic_healthy.json")
    ref.save(ref_path)
    logger.info(f"Healthy reference from {ref.n_cycles} train cycles -> {ref_path}")

    split_of = {i: name for name, idx in load_splits("hydraulic").items() for i in idx}
    cycles = load_cycles("hydraulic", split="all")
    Path("data/rationales").mkdir(parents=True, exist_ok=True)
    Path("data/qa").mkdir(parents=True, exist_ok=True)

    rt_total = rt_ok = 0
    rationales: list[tuple[int, str]] = []
    with (
        open("data/rationales/hydraulic.jsonl", "w", encoding="utf-8") as fr,
        open("data/qa/hydraulic.jsonl", "w", encoding="utf-8") as fq,
    ):
        for i, c in enumerate(cycles):
            feats = ex.extract(c)
            r = build_joint_rationale(c, feats, ref, links, seed=0)
            claims, _ = parse_claims(r.text)
            if len(claims) != len(r.claims):
                raise AssertionError(
                    f"{c.id}: parser found {len(claims)} of {len(r.claims)} claims"
                )
            for v in verify(claims, c, ex, ref, cfg, features=feats):
                rt_total += 1
                rt_ok += v.status == "verified"
            rationales.append((i, r.text))
            fr.write(
                json.dumps(
                    {
                        "cycle_id": c.id,
                        "split": split_of[i],
                        "text": r.text,
                        "claims": [{**cl.__dict__, "span": list(cl.span)} for cl in r.claims],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            for q in generate_cycle_qa(c, split_of[i], feats, ref, links, seed=i):
                fq.write(
                    json.dumps(
                        {
                            "cycle_id": q.cycle_id,
                            "split": q.split,
                            "question": q.question,
                            "answer": q.answer,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    logger.info(f"Round trip: {rt_ok}/{rt_total} claims verified")

    # Corruption tests on 1,000 random rationales: one number changed by ±20%, or one
    # direction flipped. A change counts as caught if that claim no longer verifies.
    rng = np.random.default_rng(0)
    picks = rng.choice(len(rationales), size=min(1000, len(rationales)), replace=False)
    val_caught = val_n = dir_caught = dir_n = 0
    missed: list[str] = []
    for k in picks:
        i, text = rationales[int(k)]
        c = cycles[i]
        claims, _ = parse_claims(text)
        j = int(rng.integers(0, len(claims)))
        cl = claims[j]
        clause = text[cl.span[0] : cl.span[1]]

        # value corruption
        factor = 1.2 if rng.random() < 0.5 else 0.8
        num = re.search(r"(?<=\s)[-+]?\d+(?:\.\d+)?(?=\s+\S+\s+\()", clause)
        if num:
            new_clause = (
                clause[: num.start()] + format_number(cl.value * factor) + clause[num.end() :]
            )
            bad = text[: cl.span[0]] + new_clause + text[cl.span[1] :]
            vc, _ = parse_claims(bad)
            vd = verify(vc, c, ex, ref, cfg)
            val_n += 1
            if vd[j].status != "verified":
                val_caught += 1
            elif len(missed) < 10:
                missed.append(f"{c.id}: {clause} -> {new_clause}")

        # direction corruption
        if " above healthy" in clause or " below healthy" in clause:
            flipped = clause.replace(" above healthy", " #B#").replace(
                " below healthy", " above healthy"
            )
            flipped = flipped.replace(" #B#", " below healthy")
            bad = text[: cl.span[0]] + flipped + text[cl.span[1] :]
            vc, _ = parse_claims(bad)
            vd = verify(vc, c, ex, ref, cfg)
            dir_n += 1
            dir_caught += vd[j].status != "verified"

    out = {
        "generated_by": "scripts/build_rationales.py",
        "git_sha": get_git_sha(),
        "n_rationales": len(rationales),
        "roundtrip_claims": rt_total,
        "roundtrip_verified": rt_ok,
        "roundtrip_pct": 100.0 * rt_ok / max(1, rt_total),
        "n_corrupted": val_n,
        "corruption_caught": val_caught,
        "corruption_caught_pct": 100.0 * val_caught / max(1, val_n),
        "corruption_factor": "±20% on one stated value",
        "missed_examples": missed,
        "n_direction_flipped": dir_n,
        "direction_flip_caught": dir_caught,
        "direction_flip_caught_pct": 100.0 * dir_caught / max(1, dir_n),
        "tolerance_rel": cfg.relative_tolerance,
    }
    Path("results").mkdir(exist_ok=True)
    with open("results/checker_validation.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Corruption caught {val_caught}/{val_n}; direction flips caught {dir_caught}/{dir_n}"
    )

    train_idx = [i for i, _ in rationales if split_of[i] == "train"]
    sample = rng.choice(train_idx, size=min(50, len(train_idx)), replace=False)
    with open("docs/rationale-spotcheck.md", "w", encoding="utf-8") as f:
        f.write("# Rationale spot-check (50 random train cycles, real UCI #447 data)\n\n")
        f.write(
            f"Checker round trip: {rt_ok}/{rt_total} claims verified "
            f"({out['roundtrip_pct']:.1f}%). Read each one against the physics; note any "
            "number or interpretation that looks wrong.\n\n"
        )
        for i in sorted(int(s) for s in sample):
            f.write(
                f"### `{cycles[i].id}` · labels {cycles[i].labels}\n\n```\n{rationales[i][1]}\n```\n\n"
            )


if __name__ == "__main__":
    main()
