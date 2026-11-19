"""Unit acceptance tests for HUST Bearing TimeNet connector."""

from connector.timenet_connectors.datasets.hust.hust_bearing.connector import (
    BEARING_GEOMETRIES,
    CONNECTOR,
    DEFECT_TYPES,
)


def test_hust_bearing_connector_structure() -> None:
    res = CONNECTOR.convert(seed=42)
    records = res["records"]
    splits = res["splits"]

    # Verify total recordings count
    assert len(records) > 0
    assert len(records) <= 99

    # Verify signals and sampling rate
    first = records[0]
    assert "VIB" in first["signals"]
    assert first["signals"]["VIB"]["rate_hz"] == 51200.0

    # Verify metadata fields
    assert first["defect_type"] in DEFECT_TYPES
    assert first["bearing_type"] in BEARING_GEOMETRIES

    # Verify leave-one-condition-out splits are disjoint
    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])

    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)

    # Confirm all test records belong to the held-out working condition
    for r in records:
        if r["id"] in test_set:
            assert r["working_condition"] == "C3_1800rpm_4kN"
