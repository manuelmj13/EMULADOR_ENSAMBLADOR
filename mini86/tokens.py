"""Tipos de tokens producidos por el tokenizer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """Token con su tipo, valor y ubicación en el código fuente."""

    kind: str
    value: object
    line: int
    col: int
