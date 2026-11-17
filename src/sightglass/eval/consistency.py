"""Label–rationale consistency: does the cited evidence support the stated label?

Rule (phase 05): at least one cited feature must be a kept physical link for the component,
and its TRUE deviation (recomputed from the signal) must point in the link's direction and lie
outside the healthy spread (|z| > 1) for a faulty label, or inside it (|z| <= 1) for a healthy
label.
"""

from pathlib import Path
from typing import Any

import yaml

from sightglass.eval.faithfulness import FaithfulnessConfig, Verdict
from sightglass.physics.base import HEALTHY_LEVELS


class ConsistencyChecker:
    """Checks one component paragraph against the kept links in hydraulic_links.yaml."""

    def __init__(
        self,
        links_path: str | Path = "configs/physics/hydraulic_links.yaml",
        cfg: FaithfulnessConfig | None = None,
    ):
        with open(Path(links_path), encoding="utf-8") as f:
            self.links: dict[str, list[dict[str, Any]]] = yaml.safe_load(f) or {}
        self.cfg = cfg or FaithfulnessConfig()

    def _neutral(self, v: Verdict) -> bool:
        # "Within the healthy spread": |z| <= 1 standard deviation of the healthy reference.
        return abs(v.true_z or 0.0) <= self.cfg.direction_neutral_band_sigma

    def _signed(self, v: Verdict) -> float:
        return v.true_z or 0.0

    def check(self, component: str, label_val: int, verdicts: list[Verdict]) -> bool:
        """True if the paragraph's cited, recomputed evidence supports ``label_val``."""
        kept = {lk["feature"]: lk for lk in self.links.get(component, []) if lk.get("kept", True)}
        healthy = label_val == HEALTHY_LEVELS.get(component)
        for v in verdicts:
            link = kept.get(v.feature or "")
            if link is None or v.true_value is None:
                continue
            if healthy:
                if self._neutral(v):
                    return True
            else:
                s = self._signed(v)
                if not self._neutral(v) and (s > 0) == (link["direction"] == "up"):
                    return True
        return False
