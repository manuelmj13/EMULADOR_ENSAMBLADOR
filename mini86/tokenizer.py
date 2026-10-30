"""Tokenizer para el subconjunto educativo de sintaxis Intel."""

from mini86.errors import TokenizeError
from mini86.isa import REGISTROS_VALIDOS
from mini86.tokens import Token


IDENTIFIER_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_."
IDENTIFIER_CHARS = IDENTIFIER_START + "0123456789"


def tokenize(source: str) -> list[Token]:
    """Convierte código ensamblador en tokens con posiciones 1-based."""
    tokens: list[Token] = []
    line = 1
    col = 1
    index = 0

    while index < len(source):
        char = source[index]

        if char in " \t\r":
            index += 1
            col += 1
            continue
        if char == "\n":
            tokens.append(Token("NEWLINE", "\n", line, col))
            index += 1
            line += 1
            col = 1
            continue
        if char == ";":
            while index < len(source) and source[index] != "\n":
                index += 1
                col += 1
            continue
        if char == ",":
            tokens.append(Token("COMMA", ",", line, col))
            index += 1
            col += 1
            continue
        if char == ":":
            raise TokenizeError(line, col, "unexpected ':'")

        start_col = col
        if char == "-" or char.isdigit():
            value, consumed = _read_number(source, index, line, col)
            tokens.append(Token("NUMBER", value, line, start_col))
            index += consumed
            col += consumed
            continue

        if char in IDENTIFIER_START:
            end = index + 1
            while end < len(source) and source[end] in IDENTIFIER_CHARS:
                end += 1
            value = source[index:end].lower()
            kind = "REGISTER" if value in REGISTROS_VALIDOS else "IDENTIFIER"
            token = Token(kind, value, line, start_col)
            if end < len(source) and source[end] == ":":
                tokens.append(Token("LABEL", value, line, start_col))
                tokens.append(Token("COLON", ":", line, start_col + end - index))
            else:
                tokens.append(token)
            col += end - index
            index = end
            if end < len(source) and source[end] == ":":
                index += 1
                col += 1
            continue

        raise TokenizeError(line, col, f"unexpected character {char!r}")

    tokens.append(Token("EOF", None, line, col))
    return tokens


def _read_number(source: str, index: int, line: int, col: int) -> tuple[int, int]:
    """Lee un número decimal, hexadecimal o binario, incluyendo signo."""
    start = index
    if source[index] == "-":
        index += 1
        if index == len(source) or not source[index].isdigit():
            raise TokenizeError(line, col, "expected number after '-'")

    if source[index:index + 2].lower() in {"0x", "0b"}:
        prefix = source[index:index + 2].lower()
        digit_start = index + 2
        digit_end = digit_start
        while digit_end < len(source) and source[digit_end].isalnum():
            digit_end += 1
        digits = source[digit_start:digit_end]
        valid_digits = "0123456789abcdefABCDEF" if prefix == "0x" else "01"
        if not digits or any(digit not in valid_digits for digit in digits):
            raise TokenizeError(line, col, f"invalid {prefix} number")
        value = int(digits, 16 if prefix == "0x" else 2)
        end = digit_end
    else:
        digit_end = index
        while digit_end < len(source) and source[digit_end].isalnum():
            digit_end += 1
        literal = source[index:digit_end]
        suffix = literal[-1:].lower()
        if suffix in {"h", "b"}:
            digits = literal[:-1]
            if not digits:
                raise TokenizeError(line, col, f"invalid {suffix}-suffix number")
            valid_digits = "0123456789abcdefABCDEF" if suffix == "h" else "01"
            if any(digit not in valid_digits for digit in digits):
                raise TokenizeError(line, col, f"invalid {suffix}-suffix number")
            value = int(digits, 16 if suffix == "h" else 2)
            end = digit_end
        else:
            if not literal.isdigit():
                raise TokenizeError(line, col, "invalid numeric literal")
            digits = literal
            value = int(digits, 10)
            end = digit_end

    if end < len(source) and source[end] in IDENTIFIER_CHARS:
        raise TokenizeError(line, col, "invalid numeric literal")
    if source[start] == "-":
        value = -value
    return value, end - start
