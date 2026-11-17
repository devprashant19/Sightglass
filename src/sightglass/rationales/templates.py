"""Physics-grounded reasoning templates with linguistic diversity."""

from typing import ClassVar


class HydraulicReasoningTemplates:
    """Varied physical interpretations for component faults to avoid memorization."""

    COOLER_FAIL: ClassVar[list[str]] = [
        "Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.",
        "Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.",
        "Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.",
    ]
    COOLER_REDUCED: ClassVar[list[str]] = [
        "Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.",
        "Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.",
        "Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.",
    ]
    COOLER_OPTIMAL: ClassVar[list[str]] = [
        "Operating temperatures and thermal gradient remain within optimal baseline specifications.",
        "Heat exchanger maintains expected fluid cooling delta without thermal drift.",
        "Thermal characteristics align with nominal continuous cooling performance.",
    ]

    VALVE_LAG_SEVERE: ClassVar[list[str]] = [
        "Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.",
        "Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.",
        "Transient response is severely sluggish, preventing timely transition of working pressure.",
    ]
    VALVE_LAG_SMALL: ClassVar[list[str]] = [
        "Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.",
        "A small switching delay appears during the main pressure transient, reflecting early valve degradation.",
        "Hydraulic valve exhibits slight transient lag while maintaining target pressure.",
    ]
    VALVE_OPTIMAL: ClassVar[list[str]] = [
        "Sharp pressure transient and immediate switching between sensors indicate optimal valve response.",
        "Directional valve actuates cleanly with no discernible switching hesitation.",
        "Valve switching latency remains tightly within normal healthy tolerances.",
    ]

    PUMP_LEAK_SEVERE: ClassVar[list[str]] = [
        "Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.",
        "Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.",
        "High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.",
    ]
    PUMP_LEAK_WEAK: ClassVar[list[str]] = [
        "Minor drop in delivered flow relative to motor power indicates early internal pump leakage.",
        "Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.",
        "Volumetric delivery is slightly compromised due to minor internal bypass flow.",
    ]
    PUMP_OPTIMAL: ClassVar[list[str]] = [
        "Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.",
        "Pump delivers nominal flow rate at baseline electrical input power.",
        "No internal bypassing detected; volumetric efficiency is optimal.",
    ]

    ACCUMULATOR_SEVERELY_REDUCED: ClassVar[list[str]] = [
        "Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.",
        "Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.",
        "Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.",
    ]
    ACCUMULATOR_SLIGHTLY_REDUCED: ClassVar[list[str]] = [
        "Elevated pressure ripple across working lines indicates moderate degradation of accumulator pre-charge.",
        "Slight increase in pressure oscillations indicates reduced surge dampening capacity.",
        "Hydraulic dampening shows early wear with mildly heightened ripple during load transitions.",
    ]
    ACCUMULATOR_OPTIMAL: ClassVar[list[str]] = [
        "Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.",
        "Hydraulic accumulator effectively dampens load transients with normal pre-charge.",
        "Pressure stability and surge dampening meet full design specifications.",
    ]
