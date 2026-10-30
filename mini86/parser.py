"""Parser del subconjunto educativo de sintaxis Intel."""

from mini86.ast_nodes import (
    Immediate,
    Instruction,
    Label,
    LabelRef,
    Operand,
    Program,
    Register,
)
from mini86.errors import ParseError
from mini86.isa import JCC_ALIASES, REGISTROS_VALIDOS
from mini86.tokens import Token


ARITHMETIC = {"add", "sub", "cmp"}
JUMPS = {"jmp", *JCC_ALIASES}
NO_OPERANDS = {"hlt"}
ONE_REGISTER = {"inc", "dec"}
TWO_OPERANDS = {"mov", "add", "sub", "cmp", "test"}
SUPPORTED = ARITHMETIC | JUMPS | NO_OPERANDS | ONE_REGISTER | {"mov", "test"}


def parse(tokens: list[Token]) -> Program:
    """Convierte una secuencia de tokens en un programa validado."""
    statements: list[Label | Instruction] = []
    labels: dict[str, Token] = {}
    index = 0

    while index < len(tokens):
        if tokens[index].kind in {"NEWLINE", "EOF"}:
            index += 1
            continue

        line = tokens[index].line
        line_tokens: list[Token] = []
        while index < len(tokens) and tokens[index].kind not in {"NEWLINE", "EOF"}:
            line_tokens.append(tokens[index])
            index += 1
        if not line_tokens:
            continue

        offset = 0
        if line_tokens[0].kind == "LABEL":
            if len(line_tokens) < 2 or line_tokens[1].kind != "COLON":
                _error(line_tokens[0], "invalid label")
            label_token = line_tokens[0]
            name = str(label_token.value)
            if name in labels:
                _error(label_token, f"duplicate label {name!r}")
            labels[name] = label_token
            statements.append(Label(name))
            offset = 2

        if offset == len(line_tokens):
            continue
        instruction_tokens = line_tokens[offset:]
        instruction = _parse_instruction(instruction_tokens, line)
        statements.append(instruction)

    _validate_label_references(statements, labels)
    return Program(tuple(statements))


def _parse_instruction(tokens: list[Token], line: int) -> Instruction:
    mnemonic_token = tokens[0]
    if mnemonic_token.kind != "IDENTIFIER":
        _error(mnemonic_token, "expected instruction")
    mnemonic = str(mnemonic_token.value)
    if mnemonic not in SUPPORTED:
        _error(mnemonic_token, f"unsupported instruction {mnemonic!r}")

    operand_tokens = _without_commas(tokens[1:])
    expected = _expected_operand_count(mnemonic)
    if len(operand_tokens) != expected:
        _error(
            mnemonic_token,
            f"{mnemonic} expects {expected} operand(s), got {len(operand_tokens)}",
        )

    operands = tuple(_parse_operand(token) for token in operand_tokens)
    _validate_operand_types(mnemonic, operands, mnemonic_token)
    return Instruction(mnemonic, operands, line)


def _without_commas(tokens: list[Token]) -> list[Token]:
    result: list[Token] = []
    expect_operand = True
    for token in tokens:
        if token.kind == "COMMA":
            if expect_operand:
                _error(token, "unexpected comma")
            expect_operand = True
        else:
            if not expect_operand:
                _error(token, "expected comma between operands")
            result.append(token)
            expect_operand = False
    if expect_operand and result:
        _error(tokens[-1], "expected operand after comma")
    return result


def _expected_operand_count(mnemonic: str) -> int:
    if mnemonic in NO_OPERANDS:
        return 0
    if mnemonic in ONE_REGISTER:
        return 1
    if mnemonic in TWO_OPERANDS or mnemonic == "jmp" or mnemonic in JCC_ALIASES:
        return 2 if mnemonic in TWO_OPERANDS else 1
    raise AssertionError(f"unhandled instruction: {mnemonic}")


def _parse_operand(token: Token) -> Operand:
    if token.kind == "REGISTER":
        return Register(str(token.value))
    if token.kind == "NUMBER":
        return Immediate(int(token.value))
    if token.kind == "IDENTIFIER":
        return LabelRef(str(token.value))
    _error(token, "expected register, immediate, or label")


def _validate_operand_types(
    mnemonic: str, operands: tuple[Operand, ...], token: Token
) -> None:
    if mnemonic in ONE_REGISTER and not isinstance(operands[0], Register):
        _error(token, f"{mnemonic} requires a register")
    if mnemonic in TWO_OPERANDS:
        if not isinstance(operands[0], Register):
            _error(token, f"{mnemonic} destination must be a register")
        if mnemonic == "mov" and not isinstance(operands[1], (Register, Immediate)):
            _error(token, "mov source must be a register or immediate")
        if mnemonic in ARITHMETIC | {"test"} and not isinstance(
            operands[1], (Register, Immediate)
        ):
            _error(token, f"{mnemonic} source must be a register or immediate")
    if mnemonic == "jmp" or mnemonic in JCC_ALIASES:
        if not isinstance(operands[0], LabelRef):
            _error(token, f"{mnemonic} target must be a label")


def _validate_label_references(
    statements: list[Label | Instruction], labels: dict[str, Token]
) -> None:
    for statement in statements:
        if not isinstance(statement, Instruction):
            continue
        for operand in statement.operands:
            if isinstance(operand, LabelRef) and operand.name not in labels:
                _error(
                    next(token for token in labels.values() if token.line == statement.line)
                    if any(token.line == statement.line for token in labels.values())
                    else Token("IDENTIFIER", operand.name, statement.line, 1),
                    f"undefined label {operand.name!r}",
                )


def _error(token: Token, message: str) -> None:
    raise ParseError(token.line, token.col, message)
