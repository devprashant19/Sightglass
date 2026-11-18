"""TSLM generation. Only a real, fine-tuned OpenTSLM checkpoint may produce diagnoses.

There is deliberately no fallback: an earlier version returned canned text chosen from the
true labels, which made every downstream metric meaningless. It was removed.
"""

from sightglass.data.models import Cycle
from sightglass.tslm.model import SightglassModel


class TSLMUnavailableError(RuntimeError):
    """Raised when no trained OpenTSLM model is loaded."""


def generate_diagnosis(
    model: SightglassModel,
    cycle: Cycle,
    norm_stats: dict[str, dict[str, float]],
    max_new_tokens: int = 400,
    temperature: float = 0.0,
) -> str:
    """Greedy diagnosis + rationale from a fine-tuned OpenTSLM-Flamingo model."""
    if model.is_smoke or not getattr(model, "is_opentslm", False):
        raise TSLMUnavailableError(
            "No fine-tuned OpenTSLM model is loaded. TSLM diagnoses need a GPU fine-tune "
            "(configs/train/hydraulic_flamingo_*.yaml, see phases/04-finetuning.md). The CPU smoke "
            "adapter only tests the training loop and never produces displayed predictions."
        )
    from sightglass.tslm.prompt import build_prompt_and_series

    prompt, series = build_prompt_and_series(cycle, norm_stats)
    out = model.model.generate(  # OpenTSLM API: verify against third_party/OpenTSLM
        prompt=prompt, series=series, max_new_tokens=max_new_tokens, temperature=temperature
    )
    return str(out)
