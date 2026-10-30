import pytest

from mini86.ast_nodes import Immediate, Instruction, Label, LabelRef, Program, Register
from mini86.errors import ParseError
from mini86.parser import parse
from mini86.tokenizer import tokenize


def parse_source(source: str) -> Program:
    return parse(tokenize(source))


def test_parsea_instrucciones_y_operandos() -> None:
    program = parse_source("mov eax, 42\nadd eax, ebx\ninc eax\nhlt")

    assert program.statements == (
        Instruction("mov", (Register("eax"), Immediate(42)), 1),
        Instruction("add", (Register("eax"), Register("ebx")), 2),
        Instruction("inc", (Register("eax"),), 3),
        Instruction("hlt", (), 4),
    )


def test_parsea_etiquetas_y_saltos() -> None:
    program = parse_source("inicio:\n  cmp eax, 0\n  jz fin\nfin:\n  hlt")

    assert program.statements == (
        Label("inicio"),
        Instruction("cmp", (Register("eax"), Immediate(0)), 2),
        Instruction("jz", (LabelRef("fin"),), 3),
        Label("fin"),
        Instruction("hlt", (), 5),
    )


@pytest.mark.parametrize("source", ["mov eax", "hlt eax", "inc eax, ebx", "add eax,"])
def test_rechaza_cantidad_incorrecta_de_operandos(source: str) -> None:
    with pytest.raises(ParseError):
        parse_source(source)


@pytest.mark.parametrize("source", ["inc 1", "mov 1, eax", "jmp eax", "add eax, destino"])
def test_rechaza_tipos_de_operandos_invalidos(source: str) -> None:
    with pytest.raises(ParseError):
        parse_source(source)


def test_rechaza_etiqueta_duplicada_o_no_definida() -> None:
    with pytest.raises(ParseError, match="duplicate label"):
        parse_source("loop:\nloop:\n hlt")
    with pytest.raises(ParseError, match="undefined label"):
        parse_source("jmp ausente")
