"""Main window: sidebar navigation and status on the left, the current page on the right."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import neurorock
from neurorock.app import theme
from neurorock.app.pages.placeholder import PlaceholderPage

# Every page is a placeholder for now: (title, milestone, what it will do).
PAGES = [
    (
        "Setup",
        "M0",
        "Connect a board (simulated, OpenBCI Cyton, or a replayed recording), see the live signal, "
        "and check each electrode's signal quality.",
    ),
    (
        "Calibrate",
        "M1",
        "Pick the musician and instrument, press Start, and follow the cues. The app records the "
        "calibration and tunes the instrument from it.",
    ),
    (
        "Play",
        "M1",
        "The band: tempo, key, metronome, backing beat, and one card per instrument. Drums play from "
        "muscles (EMG), bass from alpha waves, guitar from imagined movement.",
    ),
    ("Session", "M3", "Pick the musician and instrument, then play alone or join the band over MQTT."),
    ("Sound", "M1", "Levels, and which samples each instrument uses."),
    ("Settings", "M1", "Sound output, buffer size, latency, and where recordings are saved."),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroRock")
        self.resize(1280, 800)

        self.nav = QListWidget()
        self.nav.setObjectName("nav")
        self.pages = QStackedWidget()
        for title, milestone, description in PAGES:
            self.nav.addItem(title)
            self.pages.addWidget(PlaceholderPage(title, milestone, description))
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(0, 0, 0, 14)
        side.setSpacing(4)
        brand = QLabel(f'Neuro<span style="color:{theme.ACCENT}">Rock</span>')
        brand.setObjectName("brand")
        side.addWidget(brand)
        side.addWidget(self.nav, 1)
        for text in ("No board", "Sound off", f"v{neurorock.__version__}"):
            chip = QLabel(
                text if text.startswith("v") else f'<span style="color:{theme.FAINT}">●</span>&nbsp; {text}'
            )
            chip.setObjectName("chip")
            side.addWidget(chip)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Not connected")

    def show_page(self, title: str) -> None:
        for row in range(self.nav.count()):
            if self.nav.item(row).text() == title:
                self.nav.setCurrentRow(row)
