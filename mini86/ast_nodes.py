"""Nodos inmutables del árbol sintáctico del ensamblador."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Register:
    name: str


@dataclass(frozen=True)
class Immediate:
    value: int


@dataclass(frozen=True)
class LabelRef:
    name: str


@dataclass(frozen=True)
class Label:
    name: str


Operand = Register | Immediate | LabelRef


@dataclass(frozen=True)
class Instruction:
    mnemonic: str
    operands: tuple[Operand, ...]
    line: int


@dataclass(frozen=True)
class Program:
    statements: tuple[Label | Instruction, ...]
