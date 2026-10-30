from pathlib import Path

import pytest

from mini86.executor import Executor
from mini86.parser import parse
from mini86.tokenizer import tokenize


EXAMPLES = Path(__file__).parents[1] / "examples"


def run_example(name: str) -> Executor:
    source = (EXAMPLES / name).read_text(encoding="utf-8")
    executor = Executor(parse(tokenize(source)))
    for _ in range(100):
        if executor.step().estado == "halted":
            return executor
    pytest.fail(f"{name} no terminó")


@pytest.mark.parametrize(
    ("name", "register", "value"),
    [
        ("01_salto_incondicional.asm", "eax", 1),
        ("02_comparacion_basica.asm", "ebx", 1),
        ("03_overflow_con_signo.asm", "ebx", 1),
        ("04_flag_de_carry.asm", "ebx", 1),
        ("05_inc_no_toca_carry.asm", "ebx", 1),
        ("06_loop_con_dec.asm", "eax", 3),
        ("07_test_vs_cmp.asm", "ebx", 1),
    ],
)
def test_ejemplos_terminan_con_estado_esperado(
    name: str, register: str, value: int
) -> None:
    executor = run_example(name)

    assert executor.cpu.read_register(register) == value


def test_ejemplo_overflow_con_signo() -> None:
    executor = run_example("03_overflow_con_signo.asm")

    assert executor.cpu.registers["eax"] == 0x80000000
    assert executor.cpu.flags["OF"] is True
    assert executor.cpu.flags["SF"] is True
    assert executor.cpu.flags["CF"] is False
