from typing import Optional


def identity(inp: float) -> float:
    return inp


def convert_fahrenheit_to_celsius(inp: float) -> float:
    return (inp - 32) * 5 / 9


UNIT_LU = {
    '°C': identity,
    '℃': identity,
    '℉': convert_fahrenheit_to_celsius,
    '°F': convert_fahrenheit_to_celsius,
    '%RH': identity,
}


def to_float(inp: str, unit: str, multiplier: float = 1.0) -> Optional[float]:
    """Converts to Celcius if the input is Fahrenheit. Humidity or Celcius will
    be only be converted to float. (units: C, F or %RH)
    """
    unit_func = UNIT_LU.get(unit, lambda a: a)
    try:
        value = float(inp) * multiplier
        return unit_func(value)
    except Exception:
        return
