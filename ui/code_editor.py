"""Editor de código fuente con resaltado de la línea actual."""

from PyQt6.QtGui import QColor, QTextFormat
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit


class CodeEditor(QPlainTextEdit):
    """Editor sencillo para código ensamblador."""

    def highlight_line(self, line: int | None) -> None:
        """Resalta una línea 1-based, o limpia el resaltado."""
        if line is None or line < 1:
            self.setExtraSelections([])
            return
        block = self.document().findBlockByLineNumber(line - 1)
        if not block.isValid():
            self.setExtraSelections([])
            return
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#fff3cd"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.setPosition(block.position())
        selection.cursor.movePosition(
            selection.cursor.MoveOperation.EndOfBlock,
            selection.cursor.MoveMode.KeepAnchor,
        )
        self.setExtraSelections([selection])
