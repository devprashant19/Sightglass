"""The Sightglass engine: the diagnosis the dashboard and the API show.

  1. Physics features are extracted from the cycle's native-rate signals.
  2. LightGBM (B1, tuned on val) predicts the four component labels from those features.
  3. The rationale engine explains the PREDICTED labels with evidence clauses computed from the
     same cycle and the per-component healthy reference (train split only).
  4. The rationale text is parsed like any model output and every claim is verified against the
     signal; the consistency checker tests whether the evidence supports each label.

This is not the TSLM. The TSLM fine-tune is pending (needs a GPU); when it exists, its output
goes through steps 4 unchanged.
"""

import pickle
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from sightglass.baselines.lightgbm_baseline import LightGBMBaseline
from sightglass.data.loader import load_cycles
from sightglass.data.models import Cycle
from sightglass.eval.consistency import ConsistencyChecker
from sightglass.eval.faithfulness import FaithfulnessConfig, Verdict, parse_claims, verify
from sightglass.export.perturb import apply_all
from sightglass.physics.base import Feature, HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import COMPONENT_NAMES, COMPONENTS, build_joint_rationale
from sightglass.rationales.parse import parse_diagnosis

MODEL_NAME = "LightGBM on physics features + Sightglass rationale engine"
LINKS_PATH = "configs/physics/hydraulic_links.yaml"
ENGINE_PATH = Path("data/models/engine.pkl")


def load_links(path: str | Path = LINKS_PATH) -> dict[str, list[dict[str, Any]]]:
    with open(path, encoding="utf-8") as f:
        links: dict[str, list[dict[str, Any]]] = yaml.safe_load(f) or {}
    return {c: [lk for lk in v if lk.get("kept", True)] for c, v in links.items()}


def fit_reference(
    cycles: list[Cycle], feats: list[dict[str, Feature]], links: dict[str, list[dict[str, Any]]]
) -> HealthyReference:
    return HealthyReference.fit_per_component(
        feats,
        [c.labels for c in cycles],
        links,
        stable_list=[int(c.meta.get("stable_flag", 0)) for c in cycles],
        build_hash="uci447",
    )


class Engine:
    def __init__(
        self,
        clf: LightGBMBaseline,
        ref: HealthyReference,
        links: dict[str, list[dict[str, Any]]],
        synthetic: bool = False,
    ) -> None:
        self.clf = clf
        self.ref = ref
        self.links = links
        self.synthetic = synthetic
        self.extractor = HydraulicExtractor()
        self.cfg = FaithfulnessConfig.load()
        self.checker = ConsistencyChecker(LINKS_PATH, self.cfg)

    # ---------- training / persistence ----------
    @classmethod
    def train(cls, seed: int = 0, synthetic: bool | None = None) -> "Engine":
        train = load_cycles("hydraulic", split="train", synthetic=synthetic)
        val = load_cycles("hydraulic", split="val", synthetic=synthetic)
        ex = HydraulicExtractor()
        ft = [ex.extract(c) for c in train]
        fv = [ex.extract(c) for c in val]
        links = load_links()
        ref = fit_reference(train, ft, links)
        clf = LightGBMBaseline(name="sightglass_engine")
        clf.fit_matrix(
            clf.matrix_from_features(ft),
            [c.labels for c in train],
            clf.matrix_from_features(fv),
            [c.labels for c in val],
            seed,
        )
        return cls(clf, ref, links, synthetic=bool(train and train[0].meta.get("synthetic")))

    def save(self, path: str | Path = ENGINE_PATH) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(
                {
                    "clf": self.clf,
                    "ref": self.ref,
                    "links": self.links,
                    "synthetic": self.synthetic,
                },
                f,
            )

    @classmethod
    def load(cls, path: str | Path = ENGINE_PATH) -> "Engine":
        with open(path, "rb") as f:
            d = pickle.load(f)  # local file written by Engine.save
        return cls(d["clf"], d["ref"], d["links"], d.get("synthetic", False))

    # ---------- inference ----------
    def predict_labels(self, feats: dict[str, Feature]) -> tuple[dict[str, int], dict[str, Any]]:
        labels, probs = self.clf.predict_matrix(self.clf.matrix_from_features([feats]))[0]
        return labels, probs

    def diagnose(
        self, cycle: Cycle, perturbations: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Diagnosis in the dashboard's cycle-file ``prediction`` shape."""
        t0 = time.perf_counter()
        c = apply_all(cycle, perturbations)
        feats = self.extractor.extract(c)
        labels, probs = self.predict_labels(feats)
        rat = build_joint_rationale(c, feats, self.ref, self.links, labels=labels)
        claims, unparsed = parse_claims(rat.text)
        verdicts = verify(claims, c, self.extractor, self.ref, self.cfg, features=feats)

        def comp_of(span: tuple[int, int]) -> str:
            for p in rat.paragraphs:
                if p.span[0] <= span[0] < p.span[1]:
                    return p.component
            return ""

        by_comp: dict[str, list[Verdict]] = {k: [] for k in COMPONENTS}
        out_claims = []
        for v in verdicts:
            comp = comp_of(v.claim.span)
            by_comp.setdefault(comp, []).append(v)
            out_claims.append(claim_json(v, comp, self.ref))
        consistency = {k: self.checker.check(k, labels[k], by_comp.get(k, [])) for k in COMPONENTS}
        return {
            "model": MODEL_NAME,
            "labels": {
                k: {"value": labels[k], "name": COMPONENT_NAMES[k][labels[k]]} for k in COMPONENTS
            },
            "confidence": {k: round(max(probs[k].values()), 4) for k in COMPONENTS},
            "rationale": rat.text,
            "paragraphs": [
                {
                    "component": p.component,
                    "label_value": p.label_value,
                    "label_name": p.label_name,
                    "text": rat.text[p.span[0] : p.span[1]],
                    "span": list(p.span),
                }
                for p in rat.paragraphs
            ],
            "claims": out_claims,
            "unparsed_numbers": unparsed,
            "consistency": consistency,
            "perturbations": c.meta.get("perturbations", []),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "_features": feats,
        }

    def check_rationale(self, cycle: Cycle, text: str, model: str) -> dict[str, Any]:
        """Check a rationale another model wrote, in the dashboard's ``prediction`` shape.

        The labels are read from the text (``None`` when a line is missing or names no level),
        and every claim is checked with this engine's extractor, reference and tolerances.
        """
        parsed = parse_diagnosis(text)
        feats = self.extractor.extract(cycle)
        claims, unparsed = parse_claims(text)
        verdicts = verify(claims, cycle, self.extractor, self.ref, self.cfg, features=feats)

        def comp_of(span: tuple[int, int]) -> str:
            for k, (a, b) in parsed.paragraphs.items():
                if a <= span[0] < b:
                    return k
            return ""

        by_comp: dict[str, list[Verdict]] = {k: [] for k in COMPONENTS}
        out_claims = []
        for v in verdicts:
            comp = comp_of(v.claim.span)
            by_comp.setdefault(comp, []).append(v)
            out_claims.append(claim_json(v, comp, self.ref))
        names: dict[str, str | None] = {}
        consistency: dict[str, bool] = {}
        for k in COMPONENTS:
            lab = parsed.labels[k]
            names[k] = None if lab is None else COMPONENT_NAMES[k][lab]
            consistency[k] = lab is not None and self.checker.check(k, lab, by_comp.get(k, []))
        return {
            "model": model,
            "labels": {k: {"value": parsed.labels[k], "name": names[k]} for k in COMPONENTS},
            "rationale": text,
            "paragraphs": [
                {
                    "component": k,
                    "label_value": parsed.labels[k],
                    "label_name": names[k],
                    "text": text[a:b],
                    "span": [a, b],
                }
                for k, (a, b) in sorted(parsed.paragraphs.items(), key=lambda kv: kv[1][0])
            ],
            "claims": out_claims,
            "unparsed_numbers": unparsed,
            "consistency": consistency,
        }


def sig4(x: float | None) -> float | None:
    """Round to 4 significant figures for display files."""
    if x is None or not np.isfinite(x):
        return None
    return float(f"{x:.4g}")


def claim_json(v: Verdict, component: str, ref: HealthyReference) -> dict[str, Any]:
    cl = v.claim
    return {
        "span": list(cl.span),
        "component": component,
        "sensor": cl.sensor,
        "feature": v.feature,
        "quantity": cl.quantity,
        "stated": {
            "value": cl.value,
            "unit": cl.unit,
            "direction": cl.direction,
            "pct": cl.pct,
            "sigma": cl.sigma,
            "basis": cl.basis,
        },
        "true": {"value": sig4(v.true_value), "pct": sig4(v.true_pct), "z": sig4(v.true_z)},
        "reference": (
            {"mean": sig4(ref.mean.get(v.feature)), "std": sig4(ref.std.get(v.feature))}
            if v.feature
            else None
        ),
        "status": v.status,
        "value_ok": bool(v.value_ok),
        "direction_ok": bool(v.direction_ok),
        "window": list(v.window) if v.window else None,
    }
