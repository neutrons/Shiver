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

        data = QLabel()
        data.setPixmap(get_icon("data").pixmap(QSize(10, 14)))
        layout.addRow(data, QLabel("Selected data workspace"))

        data_u = QLabel()
        data_u.setPixmap(get_icon("unpolarized data").pixmap(QSize(40, 14)))
        layout.addRow(data_u, QLabel("Selected unpolarized data workspace"))

        data_nsf = QLabel()
        data_nsf.setPixmap(get_icon("polarized nsf data").pixmap(QSize(40, 14)))
        layout.addRow(data_nsf, QLabel("Selected no spinflip polarized data workspace"))

        data_sf = QLabel()
        data_sf.setPixmap(get_icon("polarized sf data").pixmap(QSize(40, 14)))
        layout.addRow(data_sf, QLabel("Selected spinflip polarized data workspace"))

        bkg = QLabel()
        bkg.setPixmap(get_icon("background").pixmap(QSize(10, 14)))
        layout.addRow(bkg, QLabel("Selected background workspace"))

        bkg_p_1 = QLabel()
        bkg_p_1.setPixmap(get_icon("background polarized 1").pixmap(QSize(34, 14)))
        layout.addRow(bkg_p_1, QLabel("First selected polarized background workspace"))

        bkg_p_2 = QLabel()
        bkg_p_2.setPixmap(get_icon("background polarized 2").pixmap(QSize(34, 14)))
        layout.addRow(bkg_p_2, QLabel("Second selected polarized background workspace"))

        self.setLayout(layout)


def get_icon(name: str) -> QIcon:  # pylint: disable=too-many-return-statements
    """return a icon for the given name"""
    if name == "data":
        return QIcon(
            QPixmap(
                ["5 7 2 1", "N c None", ". c #0000FF", "...NN", ".NN.N", ".NNN.", ".NNN.", ".NNN.", ".NN.N", "...NN"]
            ).scaled(QSize(10, 14))
        )

    if name == "unpolarized data":
        return QIcon(
            QPixmap(
                [
                    "20 7 2 1",
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
            ).scaled(QSize(40, 14))
        )

    if name == "polarized nsf data":
        return QIcon(
            QPixmap(
                [
                    "22 7 2 1",
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
            ).scaled(QSize(40, 14))
        )

    if name == "polarized sf data":
        return QIcon(
            QPixmap(
                [
                    "20 7 2 1",
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
            ).scaled(QSize(40, 14))
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

    if name == "background polarized 1":
        return QIcon(
            QPixmap(
                [
                    "17 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "....NNNNNNNNNNNN",
                    ".NNN.NNNNNNNNNNN",
                    ".NNN.NN...NNN.NN",
                    "....NN.NNN.N..NN",
                    ".NNN.N.NNN.NN.NN",
                    ".NNN.N....NNN.NN",
                    "....NN.NNNNN...N",
                ]
            ).scaled(QSize(34, 14))
        )

    if name == "background polarized 2":
        return QIcon(
            QPixmap(
                [
                    "17 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "....NNNNNNNNNNNN",
                    ".NNN.NNNNNNNNNNN",
                    ".NNN.NN...NNN..N",
                    "....NN.NNN.N.NN.",
                    ".NNN.N.NNN.NNN.N",
                    ".NNN.N....NNN.NN",
                    "....NN.NNNNN....",
                ]
            ).scaled(QSize(34, 14))
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
