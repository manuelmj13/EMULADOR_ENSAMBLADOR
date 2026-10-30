"""Ejecución paso a paso del AST sobre una CPU virtual."""

from dataclasses import dataclass

from mini86.ast_nodes import Immediate, Instruction, Label, LabelRef, Operand, Program, Register
from mini86.errors import ExecutionError
from mini86.evaluator import evaluar_jcc, ejecutar_alu
from mini86.machine import CPU


@dataclass(frozen=True)
class Snapshot:
    """Estado observable de la CPU después de un paso de ejecución."""

    pc: int
    regs: dict[str, int]
    flags: dict[str, bool]
    ultima_comparacion: tuple[int, int] | None
    proxima_instruccion: Instruction | None
    estado: str


class Executor:
    """Ejecuta un programa sobre una CPU, una instrucción por paso."""

    def __init__(self, program: Program, cpu: CPU | None = None) -> None:
        self.program = program
        self.cpu = cpu or CPU()
        self._labels = {
            statement.name: index
            for index, statement in enumerate(program.statements)
            if isinstance(statement, Label)
        }
        self.ultima_comparacion: tuple[int, int] | None = None

    def step(self) -> Snapshot:
        """Ejecuta la instrucción actual y devuelve el nuevo snapshot."""
        if self.cpu.halted:
            return self.snapshot("halted")
        self._skip_labels()
        if self.cpu.eip >= len(self.program.statements):
            self.cpu.halted = True
            return self.snapshot("finished")

        statement = self.program.statements[self.cpu.eip]
        if not isinstance(statement, Instruction):
            raise ExecutionError("expected instruction at current program counter")
        self._execute_instruction(statement)
        if not self.cpu.halted and self.cpu.eip == statement_index(self.program, statement):
            self.cpu.eip += 1
        self._skip_labels()
        return self.snapshot("halted" if self.cpu.halted else "ready")

    def snapshot(self, estado: str | None = None) -> Snapshot:
        """Crea un snapshot del estado actual sin exponer diccionarios mutables."""
        self._skip_labels()
        next_instruction = (
            self.program.statements[self.cpu.eip]
            if self.cpu.eip < len(self.program.statements)
            and isinstance(self.program.statements[self.cpu.eip], Instruction)
            else None
        )
        return Snapshot(
            pc=self.cpu.eip,
            regs=dict(self.cpu.registers),
            flags=dict(self.cpu.flags),
            ultima_comparacion=self.ultima_comparacion,
            proxima_instruccion=next_instruction,
            estado=estado or ("halted" if self.cpu.halted else "ready"),
        )

    def _execute_instruction(self, instruction: Instruction) -> None:
        mnemonic = instruction.mnemonic
        operands = instruction.operands
        if mnemonic == "hlt":
            self.cpu.halted = True
            return
        if mnemonic == "mov":
            self.cpu.write_register(
                _register_name(operands[0]), self._resolve_value(operands[1])
            )
            return
        if mnemonic in {"add", "sub", "inc", "dec", "cmp", "test"}:
            destination = self._resolve_value(operands[0])
            source = 1 if mnemonic in {"inc", "dec"} else self._resolve_value(operands[1])
            if mnemonic in {"inc", "dec"}:
                source = 1
            result, flags = ejecutar_alu(mnemonic, destination, source)
            if mnemonic not in {"cmp", "test"}:
                self.cpu.write_register(_register_name(operands[0]), result)
            if mnemonic in {"cmp", "test"}:
                self.ultima_comparacion = (destination, source)
            self._update_flags(flags)
            return
        if mnemonic == "jmp" or mnemonic in {
            "je", "jz", "jne", "jnz", "jg", "jnle", "jge", "jnl",
            "jl", "jnge", "jle", "jng", "ja", "jnbe", "jae", "jnb",
            "jnc", "jb", "jnae", "jc", "jbe", "jna", "js", "jns", "jo", "jno",
        }:
            target = _label_name(operands[0])
            should_jump = mnemonic == "jmp" or evaluar_jcc(mnemonic, self.cpu.flags)
            if should_jump:
                self.cpu.eip = self._labels[target]
            return
        raise ExecutionError(f"unsupported instruction {mnemonic!r}")

    def _resolve_value(self, operand: Operand) -> int:
        if isinstance(operand, Register):
            return self.cpu.read_register(operand.name)
        if isinstance(operand, Immediate):
            return operand.value
        raise ExecutionError(f"operand {operand!r} is not a value")

    def _update_flags(self, flags: dict[str, bool]) -> None:
        for name, value in flags.items():
            self.cpu.write_flag(name, value)

    def _skip_labels(self) -> None:
        while (
            self.cpu.eip < len(self.program.statements)
            and isinstance(self.program.statements[self.cpu.eip], Label)
        ):
            self.cpu.eip += 1


def _register_name(operand: Operand) -> str:
    if not isinstance(operand, Register):
        raise ExecutionError("destination must be a register")
    return operand.name


def _label_name(operand: Operand) -> str:
    if not isinstance(operand, LabelRef):
        raise ExecutionError("jump target must be a label")
    return operand.name


def statement_index(program: Program, statement: Instruction) -> int:
    """Obtiene el índice de una instrucción; las instrucciones son objetos únicos."""
    for index, current in enumerate(program.statements):
        if current is statement:
            return index
    raise ExecutionError("instruction is not part of the program")
