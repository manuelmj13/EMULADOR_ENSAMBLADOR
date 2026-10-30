import pytest

from mini86.errors import ExecutionError
from mini86.machine import CPU


def test_cpu_inicializa_registros_flags_y_control() -> None:
    cpu = CPU()

    assert cpu.registers == {
        "eax": 0,
        "ebx": 0,
        "ecx": 0,
        "edx": 0,
        "esi": 0,
        "edi": 0,
        "esp": 0,
        "ebp": 0,
    }
    assert cpu.flags == {"CF": False, "ZF": False, "SF": False, "OF": False, "PF": False}
    assert cpu.eip == 0
    assert cpu.halted is False


def test_cpu_normaliza_registros_y_actualiza_flags() -> None:
    cpu = CPU()
    cpu.write_register("eax", -1)
    cpu.write_flag("CF", 1)

    assert cpu.read_register("eax") == 0xFFFFFFFF
    assert cpu.read_flag("CF") is True


@pytest.mark.parametrize("operation", ["read_register", "write_register", "read_flag", "write_flag"])
def test_cpu_rechaza_nombres_desconocidos(operation: str) -> None:
    cpu = CPU()

    with pytest.raises(ExecutionError):
        getattr(cpu, operation)("invalid", 1) if operation.startswith("write") else getattr(cpu, operation)("invalid")
