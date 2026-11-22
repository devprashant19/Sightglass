"""The soft-prompt TSLM: patching, encoder shapes, the loss mask and the diagnosis parser.

Uses synthetic cycles and a tiny randomly initialised language model, so it needs no download.
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from sightglass.data.loader import generate_synthetic_hydraulic_cycle  # noqa: E402
from sightglass.tslm.softprompt import (  # noqa: E402
    N_PATCH,
    SoftPromptTSLM,
    cycle_patches,
    fit_norm,
    patch_lengths,
)


def _cycles(n: int = 3) -> list:
    rng = np.random.default_rng(0)
    return [generate_synthetic_hydraulic_cycle(i, rng) for i in range(n)]


def test_patches_keep_native_rates() -> None:
    cs = _cycles()
    lengths = patch_lengths(cs[0])
    for s, n in lengths.items():
        assert n * N_PATCH == len(cs[0].signals[s].values)
    p = cycle_patches(cs[0], fit_norm(cs), lengths)
    assert all(v.shape == (N_PATCH, lengths[s] + 2) for s, v in p.items())
    assert all(np.isfinite(v).all() for v in p.values())


def _tiny_model(lengths: dict[str, int]) -> SoftPromptTSLM:
    cfg = transformers.LlamaConfig(
        vocab_size=64,
        hidden_size=32,
        intermediate_size=64,
        num_hidden_layers=1,
        num_attention_heads=2,
        num_key_value_heads=2,
        eos_token_id=1,
    )
    torch.manual_seed(0)
    lm = transformers.LlamaForCausalLM(cfg)
    return SoftPromptTSLM(lm, lengths, torch.tensor([5, 6, 7]))


def test_loss_ignores_padding_and_backpropagates_into_encoder() -> None:
    cs = _cycles(2)
    lengths = patch_lengths(cs[0])
    model = _tiny_model(lengths)
    norm = fit_norm(cs)
    per = [cycle_patches(c, norm, lengths) for c in cs]
    patches = {s: torch.from_numpy(np.stack([p[s] for p in per])) for s in lengths}
    ids = torch.tensor([[10, 11, 12, 1], [10, 11, 1, 1]])
    mask = torch.tensor([[1, 1, 1, 1], [1, 1, 1, 0]])
    loss = model(patches, ids, mask)
    loss.backward()
    assert torch.isfinite(loss)
    assert model.encoder.proj[str(lengths["PS1"])].weight.grad.abs().sum() > 0
    # Changing a padded target token must not change the loss.
    ids2 = ids.clone()
    ids2[1, 3] = 20
    assert torch.allclose(model(patches, ids2, mask), loss)
