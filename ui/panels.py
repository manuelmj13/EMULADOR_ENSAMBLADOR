"""Paneles de información de la CPU."""

from PyQt6.QtWidgets import QFormLayout, QLabel, QGroupBox, QVBoxLayout, QWidget


class StatePanel(QWidget):
    """Muestra registros, flags, comparación y estado de ejecución."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.registers = QFormLayout()
        self.flags = QFormLayout()
        registers_box = QGroupBox("Registros")
        registers_box.setLayout(self.registers)
        flags_box = QGroupBox("Flags")
        flags_box.setLayout(self.flags)
        layout.addWidget(registers_box)
        layout.addWidget(flags_box)
        self.comparison_label = QLabel("Última comparación: -")
        self.state_label = QLabel("Estado: -")
        layout.addWidget(self.comparison_label)
        layout.addWidget(self.state_label)
        self._register_labels: dict[str, QLabel] = {}
        self._flag_labels: dict[str, QLabel] = {}
        for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
            label = QLabel("0x00000000")
            self._register_labels[name] = label
            self.registers.addRow(name, label)
        for name in ("CF", "ZF", "SF", "OF", "PF"):
            label = QLabel("0")
            self._flag_labels[name] = label
            self.flags.addRow(name, label)

    def update_state(
        self,
        regs: dict[str, int],
        flags: dict[str, bool],
        comparison: tuple[int, int] | None,
        state: str,
    ) -> None:
        """Actualiza los valores mostrados."""
        for name, label in self._register_labels.items():
            label.setText(f"0x{regs[name]:08X}")
        for name, label in self._flag_labels.items():
            label.setText(str(int(flags[name])))
        comparison_text = "-" if comparison is None else f"{comparison[0]} vs {comparison[1]}"
        self.comparison_label.setText(f"Última comparación: {comparison_text}")
        self.state_label.setText(f"Estado: {state}")
