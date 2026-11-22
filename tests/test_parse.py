"""Reading the four component lines of a rationale written by a model."""

from sightglass.rationales.parse import parse_diagnosis


def test_parse_diagnosis_reads_labels_and_rejects_unknown_levels() -> None:
    text = (
        "Cooler: reduced efficiency. Evidence: TS4 mean temperature 45.1 °C (8% above healthy).\n"
        "Valve: small lag. Evidence: none.\n"
        "Pump leakage: a bit leaky. Evidence: none.\n"
    )
    p = parse_diagnosis(text)
    assert p.labels["cooler_condition"] == 20
    assert p.labels["valve_condition"] == 90
    assert p.labels["pump_leakage"] is None  # not a level name
    assert p.labels["accumulator_pressure"] is None  # line missing
    a, b = p.paragraphs["cooler_condition"]
    assert text[a:b].startswith("Cooler:")
