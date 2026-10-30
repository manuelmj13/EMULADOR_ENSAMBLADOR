from mini86.isa import (
    FLAGS_POR_INSTRUCCION,
    JCC_ALIASES,
    REGISTROS_VALIDOS,
)


def test_registros_validos() -> None:
    assert REGISTROS_VALIDOS == {
        "eax",
        "ebx",
        "ecx",
        "edx",
        "esi",
        "edi",
        "esp",
        "ebp",
    }


def test_flags_por_instruccion() -> None:
    assert FLAGS_POR_INSTRUCCION["add"] == {"CF", "ZF", "SF", "OF", "PF"}
    assert FLAGS_POR_INSTRUCCION["sub"] == {"CF", "ZF", "SF", "OF", "PF"}
    assert FLAGS_POR_INSTRUCCION["inc"] == {"ZF", "SF", "OF", "PF"}
    assert FLAGS_POR_INSTRUCCION["dec"] == {"ZF", "SF", "OF", "PF"}
    assert FLAGS_POR_INSTRUCCION["cmp"] == {"CF", "ZF", "SF", "OF", "PF"}
    assert FLAGS_POR_INSTRUCCION["test"] == {"ZF", "SF", "PF"}
    assert FLAGS_POR_INSTRUCCION["mov"] == set()


def test_aliases_de_jcc() -> None:
    assert JCC_ALIASES["jz"] == "je"
    assert JCC_ALIASES["jnz"] == "jne"
    assert JCC_ALIASES["jnle"] == "jg"
    assert JCC_ALIASES["jnl"] == "jge"
    assert JCC_ALIASES["jnge"] == "jl"
    assert JCC_ALIASES["jng"] == "jle"
    assert JCC_ALIASES["jnbe"] == "ja"
    assert JCC_ALIASES["jnb"] == "jae"
    assert JCC_ALIASES["jnc"] == "jae"
    assert JCC_ALIASES["jnae"] == "jb"
    assert JCC_ALIASES["jc"] == "jb"
    assert JCC_ALIASES["jna"] == "jbe"
