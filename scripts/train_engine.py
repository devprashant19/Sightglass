"""Train the Sightglass engine on the real train split (val for tuning) and save it.

Writes data/models/engine.pkl (used by scripts/evaluate.py, scripts/export_site_data.py and the
API) and results/engine_training.json (chosen hyperparameters and reference sizes).
"""

import json
from pathlib import Path

from sightglass.engine import ENGINE_PATH, MODEL_NAME, Engine
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha

logger = get_logger("train_engine")


def main() -> None:
    engine = Engine.train(seed=0)
    engine.save(ENGINE_PATH)
    info = {
        "model": MODEL_NAME,
        "git_sha": get_git_sha(),
        "seed": 0,
        "synthetic": engine.synthetic,
        "best_params": engine.clf.best_params,
        "n_features": len(engine.clf.feature_names),
        "healthy_reference": {
            "n_train_cycles": engine.ref.n_cycles,
            "n_per_feature": engine.ref.n_per_feature,
            "basis": engine.ref.basis,
        },
        "kept_links": {c: [lk["feature"] for lk in v] for c, v in engine.links.items()},
    }
    Path("results").mkdir(exist_ok=True)
    with open("results/engine_training.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    logger.info(f"Saved {ENGINE_PATH} and results/engine_training.json")


if __name__ == "__main__":
    main()
