from typing import Optional


def idenitity(inp: float) -> float:
    return inp


def convert_fahrenheit_to_celsius(inp: float) -> float:
    return (inp - 32) * 5 / 9

UNIT_LU = {
    '°C': idenitity,
    '°F': convert_fahrenheit_to_celsius,
    '%RH': idenitity,
}


def to_float(inp: str, unit: str, multiplier: float = 1.0) -> Optional[float]:
    unit_func = UNIT_LU.get(unit, lambda a: a)
    try:
        value = float(inp) * multiplier
        return unit_func(value)
    except Exception:
        return
