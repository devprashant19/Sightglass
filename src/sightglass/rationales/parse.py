"""Read the four component lines of a rationale written by any model.

The expected form is the one the rationale builder writes:
    <Header>: <level name>. Evidence: <clauses>. <sentence>
one line per component. A missing line, or a level name that is not one of the component's
levels, gives ``None`` for that component: it is scored as wrong, never guessed.
"""

import re
from dataclasses import dataclass

from sightglass.rationales.builder import COMPONENT_HEADER, COMPONENT_NAMES, COMPONENTS


@dataclass
class ParsedDiagnosis:
    labels: dict[str, int | None]
    paragraphs: dict[str, tuple[int, int]]  # component -> character span of its line


def parse_diagnosis(text: str) -> ParsedDiagnosis:
    labels: dict[str, int | None] = dict.fromkeys(COMPONENTS)
    spans: dict[str, tuple[int, int]] = {}
    pos = 0
    for line in text.split("\n"):
        start, end = pos, pos + len(line)
        pos = end + 1
        for k, head in COMPONENT_HEADER.items():
            m = re.match(rf"\s*{re.escape(head)}:\s*([^.]+)\.", line)
            if m and k not in spans:
                spans[k] = (start, end)
                name = m.group(1).strip().lower()
                labels[k] = next(
                    (v for v, n in COMPONENT_NAMES[k].items() if n.lower() == name), None
                )
                break
    return ParsedDiagnosis(labels, spans)
