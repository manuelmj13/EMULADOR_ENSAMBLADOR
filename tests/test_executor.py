import pytest

from mini86.ast_nodes import Instruction, Program
from mini86.errors import ExecutionError
from mini86.executor import Executor
from mini86.machine import CPU
from mini86.parser import parse
from mini86.tokenizer import tokenize


def executor_source(source: str) -> Executor:
    return Executor(parse(tokenize(source)))


def run_to_halt(executor: Executor) -> None:
    for _ in range(100):
        snapshot = executor.step()
        if snapshot.estado == "halted":
            return
    raise AssertionError("program did not halt")


def test_ejecuta_mov_aritmetica_y_hlt_paso_a_paso() -> None:
    executor = executor_source("mov eax, 1\nadd eax, 2\nhlt")

    first = executor.step()
    assert first.regs["eax"] == 1
    assert first.pc == 1
    assert first.proxima_instruccion is not None

    second = executor.step()
    assert second.regs["eax"] == 3
    assert second.flags["ZF"] is False

    final = executor.step()
    assert final.estado == "halted"
    assert executor.cpu.halted is True


def test_cmp_y_salto_condicional_tomado() -> None:
    executor = executor_source(
        "mov eax, 5\n"
        "cmp eax, 5\n"
        "je iguales\n"
        "mov ebx, 0\n"
        "jmp fin\n"
        "iguales:\n"
        "mov ebx, 1\n"
        "fin:\n"
        "hlt\n"
    )

    run_to_halt(executor)

    assert executor.cpu.read_register("ebx") == 1
    assert executor.ultima_comparacion == (5, 5)
    assert executor.cpu.read_flag("ZF") is True


def test_salto_no_tomado_continua_en_la_siguiente_instruccion() -> None:
    executor = executor_source("mov eax, 1\ncmp eax, 2\nje igual\nmov ebx, 7\nigual:\nhlt")

    run_to_halt(executor)

    assert executor.cpu.read_register("ebx") == 7


def test_overflow_con_jo() -> None:
    executor = executor_source(
        "mov eax, 0x7FFFFFFF\n"
        "add eax, 1\n"
        "jo overflow\n"
        "jmp fin\n"
        "overflow:\n"
        "mov ebx, 1\n"
        "fin:\n"
        "hlt"
    )

    run_to_halt(executor)

    assert executor.cpu.read_register("eax") == 0x80000000
    assert executor.cpu.read_register("ebx") == 1
    assert executor.cpu.read_flag("OF") is True


def test_inc_dec_preservan_cf() -> None:
    cpu = CPU()
    cpu.write_flag("CF", True)
    executor = Executor(parse(tokenize("mov eax, 0\ninc eax\ndec eax\nhlt")), cpu)

    run_to_halt(executor)

    assert cpu.read_register("eax") == 0
    assert cpu.read_flag("CF") is True


def test_snapshot_no_expone_diccionarios_internos() -> None:
    executor = executor_source("mov eax, 1\nhlt")
    snapshot = executor.step()
    snapshot.regs["eax"] = 99
    snapshot.flags["ZF"] = True

    assert executor.cpu.read_register("eax") == 1
    assert executor.cpu.read_flag("ZF") is False


def test_rechaza_operacion_no_soportada() -> None:
    executor = Executor(Program((Instruction("mul", (), 1),)))

    with pytest.raises(ExecutionError):
        executor.step()
