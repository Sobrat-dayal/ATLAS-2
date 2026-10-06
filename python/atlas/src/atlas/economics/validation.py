from typing import Optional


def validate_unit_label(unit_label: Optional[str]) -> Optional[str]:
    if unit_label is None:
        return None

    unit_label = unit_label.strip()
    if not unit_label:
        return None

    if len(unit_label) > 128:
        return unit_label[:128]

    return unit_label
