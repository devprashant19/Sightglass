"""Unit acceptance tests for CARE Wind Turbine TimeNet connector."""

from connector.timenet_connectors.datasets.care.care_wind.connector import (
    CONNECTOR,
    TURBINES,
)


def test_care_wind_connector_structure() -> None:
    res = CONNECTOR.convert(seed=42)
    records = res["records"]
    splits = res["splits"]

    # Verify all turbines loaded
    assert len(records) == len(TURBINES)

    first = records[0]
    assert "gearbox_bearing_temp_c" in first["signals"]
    assert "active_power_kw" in first["signals"]

    # Verify 10-minute rate
    rate = first["signals"]["gearbox_bearing_temp_c"]["rate_hz"]
    assert abs(rate - (1.0 / 600.0)) < 1e-6

    # Verify disjoint splits by turbine
    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])

    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)

    # Test turbines hold out WTG05 & WTG06
    assert "care_WTG05" in test_set
    assert "care_WTG06" in test_set
