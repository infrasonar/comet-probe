from typing import Optional

UNIT_LU = {
    '°C': lambda a: a,
    '°F': lambda a: (a - 32) * 5 / 9,
    '%RH': lambda a: a,
}


def to_float(inp: str, unit: str, multiplier: float=1.0) -> Optional[float]:
    unit_func = UNIT_LU.get(unit, lambda a: a)
    try:
        value = unit_func(float(inp) * multiplier)
        return unit_func(value)
    except Exception:
        return
