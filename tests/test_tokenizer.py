import pytest

from mini86.errors import TokenizeError
from mini86.tokenizer import tokenize


def test_tokeniza_instruccion_registros_y_coma() -> None:
    tokens = tokenize("mov eax, ebx")

    assert [(token.kind, token.value) for token in tokens] == [
        ("IDENTIFIER", "mov"),
        ("REGISTER", "eax"),
        ("COMMA", ","),
        ("REGISTER", "ebx"),
        ("EOF", None),
    ]


def test_tokeniza_comentarios_etiquetas_y_lineas() -> None:
    tokens = tokenize("inicio:\n  jmp inicio ; no ejecutar\n")

    assert [(token.kind, token.value) for token in tokens] == [
        ("LABEL", "inicio"),
        ("COLON", ":"),
        ("NEWLINE", "\n"),
        ("IDENTIFIER", "jmp"),
        ("IDENTIFIER", "inicio"),
        ("NEWLINE", "\n"),
        ("EOF", None),
    ]


def test_tokeniza_numeros() -> None:
    tokens = tokenize("0xFF 0FFh 0b101 101b -42")

    assert [token.value for token in tokens[:-1]] == [255, 255, 5, 5, -42]


def test_rechaza_caracter_ilegal() -> None:
    with pytest.raises(TokenizeError, match="unexpected character"):
        tokenize("mov eax, @")


def test_rechaza_numero_invalido() -> None:
    with pytest.raises(TokenizeError, match="invalid 0x number"):
        tokenize("mov eax, 0xZZ")


def test_reporta_linea_y_columna() -> None:
    with pytest.raises(TokenizeError) as error:
        tokenize("\nmov eax, @")

    assert error.value.line == 2
    assert error.value.col == 10
