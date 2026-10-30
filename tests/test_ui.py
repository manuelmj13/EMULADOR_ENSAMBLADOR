from pathlib import Path

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


@pytest.fixture(scope="module")
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_ui_carga_step_y_reset(application: QApplication, tmp_path: Path) -> None:
    source_path = tmp_path / "program.asm"
    source_path.write_text("mov eax, 7\nhlt\n", encoding="utf-8")
    window = MainWindow()

    window.load_source(source_path)
    assert window.executor is not None
    assert window.executor.cpu.read_register("eax") == 0
    assert window.line_label.text() == "Línea actual: 1"

    window.step()
    assert window.executor.cpu.read_register("eax") == 7
    assert window.state_panel._register_labels["eax"].text() == "0x00000007"

    window.reset()
    assert window.executor.cpu.read_register("eax") == 0
    window.close()
