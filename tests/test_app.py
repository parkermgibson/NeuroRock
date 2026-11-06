"""The app window opens and every page in the sidebar can be shown."""

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from neurorock.app.main_window import PAGES, MainWindow
from neurorock.app.theme import apply_theme


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance() or QApplication([])
    apply_theme(instance)
    return instance


def test_window_shows_every_page(app):
    window = MainWindow()
    window.show()
    app.processEvents()
    assert [window.nav.item(row).text() for row in range(window.nav.count())] == [p[0] for p in PAGES]
    for row, (title, _, _) in enumerate(PAGES):
        window.show_page(title)
        app.processEvents()
        assert window.pages.currentIndex() == row
        texts = [label.text() for label in window.pages.currentWidget().findChildren(QLabel)]
        assert title in texts
    window.close()
