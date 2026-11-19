"""CLI entry point for training Sightglass TSLM models."""

import argparse

from sightglass.tslm.train import train


def main() -> None:
    parser = argparse.ArgumentParser(description="Sightglass Model Training CLI")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to YAML training configuration file"
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducibility")
    args = parser.parse_args()

    run_id = train(args.config, seed=args.seed)
    print(f"Training run completed successfully: {run_id}")


if __name__ == "__main__":
    main()
