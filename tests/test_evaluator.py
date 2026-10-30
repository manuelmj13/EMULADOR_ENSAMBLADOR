import pytest

from mini86.errors import ExecutionError
from mini86.evaluator import (
    calcular_flags_add,
    calcular_flags_logica,
    calcular_flags_sub,
    calcular_paridad,
    evaluar_jcc,
    ejecutar_alu,
)


def test_suma_con_carry_y_zero() -> None:
    resultado, flags = ejecutar_alu("add", 0xFFFFFFFF, 1)

    assert resultado == 0
    assert flags == {"CF": True, "ZF": True, "SF": False, "OF": False, "PF": True}


def test_suma_con_overflow_signed() -> None:
    resultado, flags = ejecutar_alu("add", 0x7FFFFFFF, 1)

    assert resultado == 0x80000000
    assert flags["OF"] is True
    assert flags["SF"] is True
    assert flags["CF"] is False


def test_resta_con_borrow_y_overflow() -> None:
    resultado, flags = ejecutar_alu("sub", 0x80000000, 1)

    assert resultado == 0x7FFFFFFF
    assert flags["CF"] is False
    assert flags["OF"] is True
    assert flags["SF"] is False


def test_cmp_devuelve_flags_sin_modificar_operandos() -> None:
    resultado, flags = ejecutar_alu("cmp", 5, 5)

    assert resultado == 0
    assert flags["ZF"] is True


def test_test_calcula_resultado_logico_y_no_cf_ni_of() -> None:
    resultado, flags = ejecutar_alu("test", 0b1010, 0b0110)

    assert resultado == 0b0010
    assert flags == {"ZF": False, "SF": False, "PF": False}


@pytest.mark.parametrize("operation", ["inc", "dec"])
def test_inc_dec_no_modifican_cf(operation: str) -> None:
    resultado, flags = ejecutar_alu(operation, 0xFFFFFFFF if operation == "inc" else 0, 1)

    assert resultado == (0 if operation == "inc" else 0xFFFFFFFF)
    assert "CF" not in flags


def test_paridad_usa_solo_el_byte_bajo() -> None:
    assert calcular_paridad(0b00000011) is True
    assert calcular_paridad(0b00000001) is False
    assert calcular_paridad(0xFFFFFF01) is False


def test_funciones_de_flags_normalizan_resultado() -> None:
    assert calcular_flags_add(0, 0, 0x100000000)["ZF"] is True
    assert calcular_flags_sub(0, 0, -0x100000000)["ZF"] is True
    assert calcular_flags_logica(0x100000000)["ZF"] is True


@pytest.mark.parametrize(
    ("mnemonic", "flags", "expected"),
    [
        ("je", {"ZF": True}, True),
        ("jz", {"ZF": True}, True),
        ("jne", {"ZF": False}, True),
        ("jg", {"ZF": False, "SF": True, "OF": True}, True),
        ("jge", {"SF": False, "OF": False}, True),
        ("jl", {"SF": True, "OF": False}, True),
        ("jle", {"ZF": True, "SF": False, "OF": True}, True),
        ("ja", {"CF": False, "ZF": False}, True),
        ("jae", {"CF": False}, True),
        ("jb", {"CF": True}, True),
        ("jbe", {"CF": False, "ZF": True}, True),
        ("js", {"SF": True}, True),
        ("jns", {"SF": False}, True),
        ("jo", {"OF": True}, True),
        ("jno", {"OF": False}, True),
    ],
)
def test_evaluar_jcc(mnemonic: str, flags: dict[str, bool], expected: bool) -> None:
    assert evaluar_jcc(mnemonic, flags) is expected


def test_evaluar_jcc_rechaza_mnemonico_desconocido() -> None:
    with pytest.raises(ExecutionError):
        evaluar_jcc("loop", {})
