"""Stand-in for pages that later milestones will build."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from neurorock.app.widgets import Card, PageHeader, hint, page_layout


class PlaceholderPage(QWidget):
    def __init__(self, title: str, milestone: str, description: str, parent: QWidget | None = None):
        super().__init__(parent)
        layout = page_layout(self)
        layout.addWidget(PageHeader(title, f"Coming in {milestone}."))
        card = Card("What this page will do")
        card.setMaximumWidth(620)
        card.body.addWidget(hint(description))
        layout.addWidget(card)
        layout.addStretch(1)
