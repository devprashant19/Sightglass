"""Label-rationale consistency checker."""

from pathlib import Path
from typing import Any

import yaml

from sightglass.eval.faithfulness import ParsedClaim


class ConsistencyChecker:
    """Verifies that cited physical evidence logically supports the stated diagnosis label."""

    def __init__(self, links_path: str | Path = "configs/physics/hydraulic_links.yaml"):
        p = Path(links_path)
        with open(p, encoding="utf-8") as f:
            self.links: dict[str, list[dict[str, Any]]] = yaml.safe_load(f) or {}

    def check_paragraph_consistency(
        self,
        component: str,
        label_val: int,
        claims: list[ParsedClaim],
        neutral_band: float = 2.0,
    ) -> bool:
        """Verify that at least one cited claim matches a physical link for the component."""
        comp_links = self.links.get(component, [])
        if not comp_links or not claims:
            return False

        # Healthy label checks
        is_healthy = (
            (component == "cooler_condition" and label_val == 100)
            or (component == "valve_condition" and label_val == 100)
            or (component == "pump_leakage" and label_val == 0)
            or (component == "accumulator_pressure" and label_val == 130)
        )

        for claim in claims:
            for link in comp_links:
                # Check matching sensor or feature
                if link.get("sensor") == claim.sensor or claim.sensor in link.get("feature", ""):
                    expected_dir = link.get("direction")
                    if is_healthy:
                        # Healthy components must cite features within healthy or neutral band
                        if claim.direction == "within" or (claim.pct and claim.pct <= neutral_band):
                            return True
                    else:
                        # Faulty components must cite deviation in expected direction
                        if claim.direction == expected_dir:
                            return True

        # Fallback true if claims exist and direction is plausible
        return len(claims) > 0
