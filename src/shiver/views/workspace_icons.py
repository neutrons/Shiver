"""PyQt widget for the workspace icons"""
from qtpy.QtWidgets import QLabel, QWidget, QFormLayout
from qtpy.QtCore import QSize
from qtpy.QtGui import QIcon, QPixmap


class IconLegend(QWidget):
    """Legend for the icons in the MDE table"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout()

        q_sample = QLabel()
        q_sample.setPixmap(get_icon("QSample").pixmap(QSize(20, 14)))
        layout.addRow(q_sample, QLabel("Q-sample workspace"))

        q_lab = QLabel()
        q_lab.setPixmap(get_icon("QLab").pixmap(QSize(20, 14)))
        layout.addRow(q_lab, QLabel("Q-lab workspace"))

        data_u = QLabel()
        data_u.setPixmap(get_icon("unpolarized").pixmap(QSize(24, 14)))
        layout.addRow(data_u, QLabel("Unpolarized data workspace"))

        data_nsf = QLabel()
        data_nsf.setPixmap(get_icon("NSF").pixmap(QSize(42, 14)))
        layout.addRow(data_nsf, QLabel("Non-SpinFlip polarized data workspace"))

        data_sf = QLabel()
        data_sf.setPixmap(get_icon("SF").pixmap(QSize(30, 14)))
        layout.addRow(data_sf, QLabel("SpinFlip polarized data workspace"))

        bkg = QLabel()
        bkg.setPixmap(get_icon("background").pixmap(QSize(10, 14)))
        layout.addRow(bkg, QLabel("background workspace"))

        self.setLayout(layout)


def get_icon(name: str) -> QIcon:  # pylint: disable=too-many-return-statements
    """return a icon for the given name"""

    if name == "unpolarized":
        return QIcon(
            QPixmap(
                [
                    "12 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "...NNNNNNNNN",
                    ".NN.NNNNNNNN",
                    ".NNN.N.NNN.N",
                    ".NNN.N.NNN.N",
                    ".NNN.N.NNN.N",
                    ".NN.NN.NNN.N",
                    "...NNNN...NN",
                ]
            ).scaled(QSize(24, 14))
        )
    if name == "NSF":
        return QIcon(
            QPixmap(
                [
                    "21 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "...NNNNNNNNNNNNNNNNNN",
                    ".NN.NNNNNNNNNNNNNNNNN",
                    ".NNN.N.NNN.NN...N....",
                    ".NNN.N..NN.N.NNNN.NNN",
                    ".NNN.N.N.N.NN..NN...N",
                    ".NN.NN.NN..NNNN.N.NNN",
                    "...NNN.NNN.N...NN.NNN",
                ]
            ).scaled(QSize(42, 14))
        )

    if name == "SF":
        return QIcon(
            QPixmap(
                [
                    "15 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "...NNNNNNNNNNNN",
                    ".NN.NNNNNNNNNNN",
                    ".NNN.NN...N....",
                    ".NNN.N.NNNN.NNN",
                    ".NNN.NN..NN...N",
                    ".NN.NNNNN.N.NNN",
                    "...NNN...NN.NNN",
                ]
            ).scaled(QSize(30, 14))
        )

    if name == "background":
        return QIcon(
            QPixmap(
                [
                    "5 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                ]
            ).scaled(QSize(10, 14))
        )

    if name == "QSample":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.NN...",
                    ".NNN.N.NNN",
                    ".N.N.NN..N",
                    ".NN.NNNNN.",
                    "N..N.N...N",
                ]
            ).scaled(QSize(20, 14))
        )

    if name == "QLab":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.N.NNN",
                    ".NNN.N.NNN",
                    ".N.N.N.NNN",
                    ".NN.NN.NNN",
                    "N..N.N....",
                ]
            ).scaled(QSize(20, 14))
        )

    raise ValueError(f"{name} doesn't correspond to a valid icon")
