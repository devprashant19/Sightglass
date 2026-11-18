"""Evaluation and verification modules for Sightglass."""

from sightglass.eval.consistency import ConsistencyChecker
from sightglass.eval.faithfulness import (
    FaithfulnessConfig,
    ParsedClaim,
    Verdict,
    parse_claims,
    verify,
)
from sightglass.eval.metrics import (
    compute_bootstrap_ci,
    compute_component_metrics,
    compute_joint_exact_match,
)

__all__ = [
    "FaithfulnessConfig",
    "ParsedClaim",
    "Verdict",
    "parse_claims",
    "verify",
    "ConsistencyChecker",
    "compute_component_metrics",
    "compute_joint_exact_match",
    "compute_bootstrap_ci",
]
