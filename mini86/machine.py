"""Estado de la CPU virtual de 32 bits."""

from mini86.errors import ExecutionError


REGISTERS = ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")
FLAGS = ("CF", "ZF", "SF", "OF", "PF")
UINT32_MASK = 0xFFFFFFFF


class CPU:
    """CPU con registros, flags, contador de programa y estado de parada."""

    def __init__(self) -> None:
        self.registers = {name: 0 for name in REGISTERS}
        self.flags = {name: False for name in FLAGS}
        self.eip = 0
        self.halted = False

    def read_register(self, name: str) -> int:
        """Devuelve el valor unsigned de un registro."""
        try:
            return self.registers[name]
        except KeyError as error:
            raise ExecutionError(f"unknown register {name!r}") from error

    def write_register(self, name: str, value: int) -> None:
        """Escribe un valor normalizado a 32 bits en un registro."""
        if name not in self.registers:
            raise ExecutionError(f"unknown register {name!r}")
        self.registers[name] = value & UINT32_MASK

    def read_flag(self, name: str) -> bool:
        """Devuelve el valor de un flag."""
        try:
            return self.flags[name]
        except KeyError as error:
            raise ExecutionError(f"unknown flag {name!r}") from error

    def write_flag(self, name: str, value: bool) -> None:
        """Actualiza un flag."""
        if name not in self.flags:
            raise ExecutionError(f"unknown flag {name!r}")
        self.flags[name] = bool(value)
