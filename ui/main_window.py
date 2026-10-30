"""Ventana principal del mini-emulador."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from mini86.errors import ExecutionError, ParseError, TokenizeError
from mini86.executor import Executor, Snapshot
from mini86.parser import parse
from mini86.tokenizer import tokenize
from ui.code_editor import CodeEditor
from ui.panels import StatePanel


class MainWindow(QMainWindow):
    """Ventana que conecta el editor con el Executor."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mini-emulador x86 IA-32")
        self.resize(1000, 650)
        self.editor = CodeEditor()
        self.state_panel = StatePanel()
        self.executor: Executor | None = None
        self._source_path: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        open_button = QPushButton("Abrir .asm")
        step_button = QPushButton("Step")
        run_button = QPushButton("Run")
        reset_button = QPushButton("Reset")
        open_button.clicked.connect(self.open_file)
        step_button.clicked.connect(self.step)
        run_button.clicked.connect(self.run)
        reset_button.clicked.connect(self.reset)
        buttons = QHBoxLayout()
        for button in (open_button, step_button, run_button, reset_button):
            buttons.addWidget(button)
        self.line_label = QLabel("Línea actual: -")
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.addWidget(self.line_label)
        editor_layout.addWidget(self.editor)
        splitter = QSplitter()
        splitter.addWidget(editor_container)
        splitter.addWidget(self.state_panel)
        splitter.setSizes([650, 350])
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(buttons)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

    def open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir programa", "", "Assembly (*.asm)")
        if not path:
            return
        try:
            self.load_source(Path(path))
        except (OSError, TokenizeError, ParseError, ExecutionError, ValueError) as error:
            QMessageBox.critical(self, "Error", str(error))

    def load_source(self, path: Path) -> None:
        """Carga, tokeniza y parsea un archivo .asm."""
        source = path.read_text(encoding="utf-8")
        self.editor.setPlainText(source)
        self._source_path = path
        self.executor = Executor(parse(tokenize(source)))
        self._show_snapshot(self.executor.snapshot())

    def reset(self) -> None:
        """Reinicia la ejecución del archivo actualmente cargado."""
        if self._source_path is not None:
            self.load_source(self._source_path)

    def step(self) -> None:
        """Ejecuta una instrucción."""
        if self.executor is None:
            return
        self._show_snapshot(self.executor.step())

    def run(self) -> None:
        """Ejecuta hasta hlt o fin del programa."""
        if self.executor is None:
            return
        for _ in range(10000):
            snapshot = self.executor.step()
            if snapshot.estado == "halted":
                self._show_snapshot(snapshot)
                return
        QMessageBox.warning(self, "Ejecución", "El programa excedió 10000 pasos.")

    def _show_snapshot(self, snapshot: Snapshot) -> None:
        self.state_panel.update_state(
            snapshot.regs,
            snapshot.flags,
            snapshot.ultima_comparacion,
            snapshot.estado,
        )
        line = snapshot.proxima_instruccion.line if snapshot.proxima_instruccion else None
        self.editor.highlight_line(line)
        self.line_label.setText(
            f"Línea actual: {line if line is not None else '-'}"
        )
