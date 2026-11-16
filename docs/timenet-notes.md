# TimeNet Architecture & Connector Notes

*Verified against upstream `OpenTSLM/TimeNet` at commit `979a0ae8894f225ecfd04a364678bea49f66bfc1`.*

## 1. Core Data Model (TimeF)
TimeNet standardizes diverse time-series formats into the **TimeF** specification:
- **`Record`:** Represents an individual entity or session (e.g., one 60-second machine load cycle). Records contain metadata and one or more `Source` objects.
- **`Source`:** A logical grouping of sensors (e.g., `pressure`, `flow`, `temperature`, `vibration`, `virtual`).
- **`Signal`:** The individual physical or virtual time-series channel. Created via `Signal.from_values(values, spec=..., name=..., time_axis=...)`.
- **`RegularAxis`:** Declares the sampling time-grid. For fixed-rate sensors, `RegularAxis.from_rate_hz(rate_hz)` defines the native sampling rate without requiring resampling to a common denominator.
- **`TimeSeriesSpec`:** Metadata for each signal type (e.g., physical unit from Pint `ureg`, description, data type `float32` or `float64`).
- **`Annotation` & `LabelSet`:** Formal definitions of classes and metadata attached to tasks.
- **`ClassificationTask`:** Binds one or more Records to ground-truth targets, label set, optional rationale, and `Split` (`Split.TRAIN`, `Split.VALIDATION`, `Split.TEST`).
- **`TimeFDataset`:** Top-level container written to disk as `manifest.json`, `control.duckdb`, and Parquet/Zarr values shards.

## 2. Connector Structure
Upstream connectors reside in `packages/timenet-connectors/src/timenet_connectors/datasets/<org>/<dataset_name>/`:
- `__init__.py`: Exports `CONNECTOR`.
- `connector.py`: Defines a class subclassing `BaseConnector`.
  - `async def download_async(self, cache_dir: Path) -> ...`: Idempotently fetches and caches raw archives using `ensure_archive(...)`.
  - `def convert(self, source_files) -> TimeFDataset`: Converts raw tab/csv/binary files into `TimeFDataset` records, signals, and tasks.
- `dataset.yaml`: Dataset card schema validated with `yaml_schema_version: 1`:
  - `dataset_id`, `dataset_version`, `name`, `description`, `license`, `source_url`, `citation`, `domains`, `tags`.
- `tests/test_connector.py`: Unit and integration tests verifying record counts, signal lengths, absence of NaNs, valid label sets, and split disjointness.

## 3. Upstream Makefile Targets
- `make check`: Runs `schemas-check`, `ruff format .`, `ruff check .`, `ty check .`.
- `make test`: Runs pytest across core modules (excluding dataset downloads).
- `make test-unit`: Fast in-memory unit tests.
- `make test-connectors`: Runs tests for individual dataset connectors in isolated environments.
- `make license-check`: Verifies no copyleft (GPL/AGPL) dependencies exist.
- `make build`: Packages `timenet` and `timenet-connectors` wheels.
