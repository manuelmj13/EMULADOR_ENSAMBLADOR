"""Interfaz de línea de comandos para el mini-emulador."""

import argparse
from pathlib import Path

from mini86.errors import ExecutionError, ParseError, TokenizeError
from mini86.executor import Executor, Snapshot
from mini86.parser import parse
from mini86.tokenizer import tokenize


def main(argv: list[str] | None = None) -> int:
    """Ejecuta un archivo .asm y muestra su progreso."""
    parser = argparse.ArgumentParser(prog="mini86")
    parser.add_argument("program", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--step", action="store_true", help="mostrar cada paso")
    mode.add_argument("--run", action="store_true", help="ejecutar hasta hlt")
    args = parser.parse_args(argv)

    try:
        source = args.program.read_text(encoding="utf-8")
        executor = Executor(parse(tokenize(source)))
        if args.step:
            while True:
                snapshot = executor.step()
                _print_snapshot(snapshot)
                if snapshot.estado == "halted":
                    break
        else:
            while executor.step().estado != "halted":
                pass
            _print_snapshot(executor.snapshot("halted"))
        return 0
    except (OSError, TokenizeError, ParseError, ExecutionError, ValueError) as error:
        parser.error(str(error))
        return 2


def _print_snapshot(snapshot: Snapshot) -> None:
    registers = " ".join(
        f"{name}={value:#010x}" for name, value in snapshot.regs.items()
    )
    flags = " ".join(
        f"{name}={int(value)}" for name, value in snapshot.flags.items()
    )
    print(f"pc={snapshot.pc} estado={snapshot.estado} {registers} {flags}")


if __name__ == "__main__":
    raise SystemExit(main())
