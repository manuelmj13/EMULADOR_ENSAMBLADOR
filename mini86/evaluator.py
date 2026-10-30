"""Evaluación pura de operaciones y condiciones del subconjunto x86."""

from mini86.errors import ExecutionError
from mini86.isa import JCC_ALIASES
from mini86.machine import UINT32_MASK

SIGN_BIT = 0x80000000


def calcular_paridad(byte_bajo: int) -> bool:
    """Devuelve True si el byte bajo tiene una cantidad par de bits a uno."""
    return (byte_bajo & 0xFF).bit_count() % 2 == 0


def calcular_flags_add(a: int, b: int, resultado: int) -> dict[str, bool]:
    """Calcula flags para una suma de 32 bits."""
    a &= UINT32_MASK
    b &= UINT32_MASK
    resultado &= UINT32_MASK
    return {
        "CF": a + b > UINT32_MASK,
        "ZF": resultado == 0,
        "SF": bool(resultado & SIGN_BIT),
        "OF": bool((~(a ^ b) & (a ^ resultado) & SIGN_BIT)),
        "PF": calcular_paridad(resultado),
    }


def calcular_flags_sub(a: int, b: int, resultado: int) -> dict[str, bool]:
    """Calcula flags para una resta de 32 bits."""
    a &= UINT32_MASK
    b &= UINT32_MASK
    resultado &= UINT32_MASK
    return {
        "CF": a < b,
        "ZF": resultado == 0,
        "SF": bool(resultado & SIGN_BIT),
        "OF": bool((a ^ b) & (a ^ resultado) & SIGN_BIT),
        "PF": calcular_paridad(resultado),
    }


def calcular_flags_logica(resultado: int) -> dict[str, bool]:
    """Calcula los flags definidos por una operación lógica."""
    resultado &= UINT32_MASK
    return {
        "ZF": resultado == 0,
        "SF": bool(resultado & SIGN_BIT),
        "PF": calcular_paridad(resultado),
    }


def ejecutar_alu(op: str, a: int, b: int) -> tuple[int, dict[str, bool]]:
    """Ejecuta una operación ALU y devuelve resultado y flags resultantes."""
    a &= UINT32_MASK
    b &= UINT32_MASK
    if op in {"add", "inc"}:
        resultado = (a + b) & UINT32_MASK
        flags = calcular_flags_add(a, b, resultado)
        if op == "inc":
            flags.pop("CF")
        return resultado, flags
    if op in {"sub", "cmp", "dec"}:
        resultado = (a - b) & UINT32_MASK
        flags = calcular_flags_sub(a, b, resultado)
        if op == "dec":
            flags.pop("CF")
        return resultado, flags
    if op == "test":
        resultado = a & b
        flags = calcular_flags_logica(resultado)
        return resultado, flags
    raise ExecutionError(f"unsupported ALU operation {op!r}")


def evaluar_jcc(mnemonic: str, flags: dict[str, bool]) -> bool:
    """Evalúa un salto condicional usando los flags proporcionados."""
    canonical = JCC_ALIASES.get(mnemonic)
    if canonical is None:
        raise ExecutionError(f"unsupported conditional jump {mnemonic!r}")

    cf = bool(flags.get("CF", False))
    zf = bool(flags.get("ZF", False))
    sf = bool(flags.get("SF", False))
    of = bool(flags.get("OF", False))
    if canonical == "je":
        return zf
    if canonical == "jne":
        return not zf
    if canonical == "jg":
        return not zf and sf == of
    if canonical == "jge":
        return sf == of
    if canonical == "jl":
        return sf != of
    if canonical == "jle":
        return zf or sf != of
    if canonical == "ja":
        return not cf and not zf
    if canonical == "jae":
        return not cf
    if canonical == "jb":
        return cf
    if canonical == "jbe":
        return cf or zf
    if canonical == "js":
        return sf
    if canonical == "jns":
        return not sf
    if canonical == "jo":
        return of
    if canonical == "jno":
        return not of
    raise ExecutionError(f"unsupported conditional jump {mnemonic!r}")
