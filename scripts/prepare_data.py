"""Download UCI #447 (SHA-256 checked) and convert it into data/build/hydraulic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from connector.timenet_connectors.datasets.uci.uci_hydraulic.connector import (  # noqa: E402
    convert,
    download,
)


def main() -> None:
    raw = download("data/raw/hydraulic")
    summary = convert(raw, "data/build/hydraulic")
    print(f"built data/build/hydraulic: {summary['n_records']} cycles, sha256 {summary['sha256']}")
    print(f"splits: {summary['splits']}")


if __name__ == "__main__":
    main()
