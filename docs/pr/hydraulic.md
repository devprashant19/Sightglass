# TimeNet pull request: uci/hydraulic

The pull request body for OpenTSLM/TimeNet, kept here for reference; the code is in [uci-hydraulic-connector.patch](uci-hydraulic-connector.patch). The make targets it names are TimeNet's, run in a TimeNet checkout, not targets of this repository.

## Title

feat(connectors): add the UCI hydraulic systems condition monitoring dataset

## Body

## What this adds

A connector for `uci/hydraulic`, UCI dataset 447,
[Condition monitoring of hydraulic systems](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems).
ZeMA gGmbH recorded 2,205 load cycles of 60 seconds on a hydraulic test rig with a working circuit
and a cooling-filtration circuit. During the run, the condition of four components (cooler, valve,
internal pump, hydraulic accumulator) was set to fixed grades. The release has 17 sensor tables
(one row per cycle) and `profile.txt` with the four grades and a stable flag per cycle.

New files, all under `packages/timenet-connectors/src/timenet_connectors/datasets/uci/`:

- `__init__.py`: the `uci` org package.
- `hydraulic/connector.py`, `hydraulic/__init__.py`: `HydraulicConnector`, a plain
  `BaseConnector`, structured like `opentslm/har-cot`.
- `hydraulic/dataset.yaml`: the card.
- `hydraulic/README.md`: signals, tasks, split counts, limitations.
- `hydraulic/tests/test_connector.py`: 20 offline tests on synthetic tables.

No `requirements.txt`: the connector reads the tables with pyarrow and numpy, which
`timenet-connectors` already depends on.

## Mapping

- `download_async` fetches the zip from the UCI static URL with `ensure_archive`, pinned to
  SHA-256 `24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2`.
- One Record per cycle. `metadata["cycle"]` is the 1-based row number, which the release uses as
  the cycle number. No absolute start time (the release states none).
- Seven Sources by sensor group, 17 Signals, each on a regular axis at its native rate. No
  resampling:

  | Source | Signals | Rate | Values | Unit |
  | --- | --- | --- | --- | --- |
  | Pressure | PS1-PS6 | 100 Hz | 6,000 | bar |
  | Motor power | EPS1 | 100 Hz | 6,000 | W |
  | Volume flow | FS1, FS2 | 10 Hz | 600 | l/min |
  | Temperature | TS1-TS4 | 1 Hz | 60 | degree Celsius |
  | Vibration | VS1 | 1 Hz | 60 | mm/s |
  | Efficiency factor | SE | 1 Hz | 60 | % |
  | Virtual | CE, CP | 1 Hz | 60 | %, kW |

- Values are float32. Every value in the release has at most five significant digits (checked on
  all 17 files), so float32 keeps each decimal value.
- Record annotations: the four grades (`cooler_condition`, `valve_condition`,
  `internal_pump_leakage`, `hydraulic_accumulator`, with units) and `stable_flag`.
- `TimeNetConnectorError` for a missing table, a row with the wrong number of values, an empty or
  non-numeric cell, a non-finite value, a row count that differs from `profile.txt`, a grade or flag
  the documentation does not list, and a train split that lacks a grade.

## Tasks

Four `ClassificationTask`s per cycle (8,820 in total), one per component. No prompt (the release
states no question). Each label set is `ordered=True`, healthy grade first, with a `name`
annotation equal to the component key, and each label's description gives the grade:

- cooler (%): full efficiency (100), reduced efficiency (20), close to total failure (3)
- valve (%): optimal switching behavior (100), small lag (90), severe lag (80), close to total
  failure (73)
- internal pump leakage: no leakage (0), weak leakage (1), severe leakage (2)
- hydraulic accumulator (bar): optimal pressure (130), slightly reduced pressure (115), severely
  reduced pressure (100), close to total failure (90)

The label text follows `documentation.txt`, with its typo "effifiency" corrected. I did not add a
joint task: it would be a single-label set of 144 combined classes, which can be rebuilt from the
four targets of a cycle.

## Splits

The release has no official partition, so the connector generates one with `StratifiedSplitter`:
`train_folds=8, validation_folds=1, test_folds=1`, seed 42 (scikit-learn 1.9.1), as for
`chengsenwang/tsqa`.

- `group_by`: the four-grade condition. The rig keeps one condition for runs of consecutive
  cycles (10 to 230 cycles per condition, 144 conditions), and neighboring cycles under one
  condition are near copies. A random split would put near copies of test cycles in train.
- `stratify_by`: the accumulator grade. The release's documentation names the accumulator the
  hardest of the four targets.
- After splitting, conversion checks that train holds every grade of every component, and raises
  `TimeNetConnectorError` if not.

Counts on the real data, read back from the built release:

| Partition | Cycles | Tasks | Conditions | Cycles with stable flag 1 |
| --- | --- | --- | --- | --- |
| train | 1,877 | 7,508 | 114 | 728 |
| validation | 164 | 656 | 15 | 14 |
| test | 164 | 656 | 15 | 14 |

Every grade of every component is in all three partitions (cycles, train / validation / test):

| Component | Grade | Train | Validation | Test |
| --- | --- | --- | --- | --- |
| cooler | 100 | 647 | 42 | 52 |
| cooler | 20 | 650 | 62 | 20 |
| cooler | 3 | 580 | 60 | 92 |
| valve | 100 | 1,017 | 54 | 54 |
| valve | 90 | 290 | 40 | 30 |
| valve | 80 | 270 | 40 | 50 |
| valve | 73 | 300 | 30 | 30 |
| pump | 0 | 1,099 | 61 | 61 |
| pump | 1 | 431 | 30 | 31 |
| pump | 2 | 347 | 73 | 72 |
| accumulator | 130 | 517 | 41 | 41 |
| accumulator | 115 | 317 | 41 | 41 |
| accumulator | 100 | 317 | 41 | 41 |
| accumulator | 90 | 726 | 41 | 41 |

## Licence and citation

CC BY 4.0, as stated on the UCI page. Citation in the card:

Helwig, N., Pignanelli, E., Schuetze, A. (2015). Condition Monitoring of a Complex Hydraulic System
Using Multivariate Statistics. In Proc. I2MTC-2015, Pisa, Italy.
https://doi.org/10.1109/I2MTC.2015.7151267

The card spells the author name "Schuetze" instead of "Schütze". On Windows, `TimeFWriter` writes
`manifest.json` with `Path.write_text` and no encoding, so a non-ASCII card produces a manifest
that the reader rejects as invalid UTF-8. No existing card has non-ASCII text either. I can switch
back to the umlaut if you prefer; CI on Linux is not affected.

## How it was tested

Windows 11, Python 3.13.15 venv from TimeNet's `sync` target, GNU Make 3.82.90 (`mingw32-make`), base `979a0ae8`.

| Command | Result |
| --- | --- |
| TimeNet's `sync` target | pass (needed `UV_LINK_MODE=copy`: hardlinks fail between the uv cache and this disk) |
| TimeNet's `check` target | ruff format and ruff check pass; `ty check` reports 5 errors, all in `packages/timenet/tests/reader/test_reader.py` (`signal.alarm`, `os.fork`, `os.WNOHANG`, `signal.SIGKILL` do not exist on Windows). The same 5 appear on the unmodified base. `ty check --python-platform linux .` and `ty check --python-version 3.11 --python-platform linux .` both pass. |
| TimeNet's `check-ci` target | the same 5 ty errors; on this Windows checkout `end-of-file-fixer` and `mixed-line-ending` also rewrite most tracked files (`core.autocrlf=true`, and the `packages/timenet/README.md` symlink is a plain file). Both are unrelated to this change. On the new files every hook passes. |
| TimeNet's `test-connectors` target | pass: all 14 connectors; `uci/hydraulic` 20 passed and `ty` clean |
| TimeNet's `test-unit` target | 1,716 passed, 1 skipped, 13 failed, 3 errors, all in `test_cache.py`, `test_cli.py` and `test_config.py` (symlinks, the home folder and POSIX paths on Windows). The same 16 fail on the unmodified base. None of them touches the new connector. |
| TimeNet's `test` target | not completed here. The core suite writes several GB of temporary files, and the test machine ran out of disk space: a first run with all workers failed with `No space left on device`. A second run with `PYTEST_WORKERS=2` was stopped at about 90 % when 2 GB were left, with 2,659 passed, 37 failed and 30 errors so far, none from `No space left on device`. TimeNet's `test` target ignores `datasets/*`, so the only tests in it that load the new connector are in `packages/timenet-connectors/tests`, run separately below. Please rely on CI for the full run. |
| TimeNet's `license-check` target | pass |

`uv run pytest packages/timenet-connectors/tests` (part of TimeNet's `test` target): 302 passed, 3 failed. The
3 are in `test_build_env.py` and `test_build_cli.py` and compare POSIX paths
(`'\\fake\\reqs.txt' == '/fake/reqs.txt'`). They fail the same way on the unmodified base.
`test_cards.py` and `test_discovery.py`, which cover every connector card, pass.

End-to-end build from the real download, with isolation (the default), from the committed branch:

```bash
uv run timenet-build build uci/hydraulic \
  --local-registry ~/timenet-work/registry --force
```

The build downloaded the 76.6 MB archive, checked it, wrote the release (94 MB on disk), and removed
the download cache. The manifest records `contains_local_changes: false` for both packages and these
counts: 2,205 records, 15,435 sources, 37,485 signals, 3 axes, 8,820 classification tasks.

Load-back through the SDK:

```python
client = timenet.TimeNet(sources=["~/timenet-work/registry"])
with client.open("uci/hydraulic") as reader:
    ds = reader.read()
```

```text
records 2205 tasks 8820
record 0 metadata {'cycle': 1}
record 0 annotations {'cooler_condition': 3, 'valve_condition': 100,
  'internal_pump_leakage': 0, 'hydraulic_accumulator': 130, 'stable_flag': 1}
  Pressure          PS1   n=6000 period_us=10000   unit=bar first=151.47
  Motor power       EPS1  n=6000 period_us=10000   unit=watt first=2411.6
  Volume flow       FS1   n=600  period_us=100000  unit=liter / minute first=8.99
  Temperature       TS1   n=60   period_us=1000000 unit=degree_Celsius first=35.57
  Vibration         VS1   n=60   period_us=1000000 unit=millimeter / second first=0.604
  Efficiency factor SE    n=60   period_us=1000000 unit=percent first=68.039
  Virtual           CE    n=60   period_us=1000000 unit=percent first=47.202
  (all 17 signals checked; PS2-PS6, FS2, TS2-TS4, CP omitted here)
tasks per split {'train': 7508, 'test': 656, 'validation': 656}
cycles per split {'train': 1877, 'test': 164, 'validation': 164}
```

The first values match the first row of `PS1.txt`, `EPS1.txt`, `FS1.txt` and `TS1.txt` in the
archive.

## Known limitations

- Validation and test hold 164 cycles each (7.4 %), not 10 %, because the conditions vary in size
  (10 to 230 cycles) and stay whole.
- 728 of the 756 cycles with stable flag 1 fell into train, so validation and test are almost all
  stable cycles. The tasks keep the unstable cycles; users can filter on the `stable_flag`
  annotation.
- The record annotations hold the task answers. They must not be passed to a model as input. The
  README says so.
- `CE` (virtual cooling efficiency) is computed from other sensors and tracks the cooler grade
  closely; a model can read the cooler grade from it. The README suggests dropping the `Virtual`
  source to measure that.
- Conversion holds all values in memory as float32, about 385 MB.
- The grades are steps of continuous degradation, as the release notes. The tasks treat them as
  ordered classes.
