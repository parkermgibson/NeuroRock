"""Start the NeuroRock desktop app: ``uv run neurorock``."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from neurorock.app.main_window import MainWindow
from neurorock.app.theme import apply_theme


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    app.setApplicationName("NeuroRock")
    app.setOrganizationName("NeuroRock")
    apply_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
