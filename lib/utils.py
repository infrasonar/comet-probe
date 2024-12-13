from typing import Optional


def to_float(inp: str) -> Optional[float]:
    try:
        return float(inp)
    except Exception:
        return
