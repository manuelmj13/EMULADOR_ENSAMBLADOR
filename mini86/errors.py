"""Errores del ensamblador educativo."""


class TokenizeError(Exception):
    """Error producido durante la tokenización del código fuente."""

    def __init__(self, line: int, col: int, message: str) -> None:
        self.line = line
        self.col = col
        self.message = message
        super().__init__(f"line {line}, column {col}: {message}")


class ParseError(Exception):
    """Error producido durante el análisis sintáctico."""

    def __init__(self, line: int, col: int, message: str) -> None:
        self.line = line
        self.col = col
        self.message = message
        super().__init__(f"line {line}, column {col}: {message}")


class ExecutionError(Exception):
    """Error producido durante la ejecución de un programa."""
