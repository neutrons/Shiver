"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
    QButtonGroup,
    QRadioButton,
)
from .data import RawData


class Generate(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        layout.setRowMinimumHeight(1, 200)
        layout.setRowMinimumHeight(2, 200)
        layout.setColumnMinimumWidth(1, 400)
        layout.setColumnMinimumWidth(2, 400)
        layout.setColumnMinimumWidth(3, 400)

        layout.addWidget(RawData(self), 1, 1)
        layout.addWidget(Oncat(self), 2, 1)
        layout.addWidget(MDEType(self), 1, 2)
        layout.addWidget(ReductionParameters(self), 2, 2)
        layout.addWidget(Buttons(self), 1, 3, 2, 1)

        self.setLayout(layout)


class Oncat(QGroupBox):
    """ONCat widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Oncat")


class MDEType(QGroupBox):
    """MDE type widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("MDE type")
        self.layout = QGridLayout()

        # mde name (label) and input
        mde_name_label = QLabel("MDE name")
        self.mde_name = QLineEdit("")
        self.mde_name.setObjectName("mde_name")
        self.layout.addWidget(mde_name_label, 0, 0)
        self.layout.addWidget(self.mde_name, 0, 1)
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)

        # output directory and browse button
        output_dir_label = QLabel("Output Folder")
        self.output_dir = QLineEdit("")
        self.output_dir.setObjectName("output_dir")
        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browse_button")
        browse_button.setToolTip("Browse for output folder")
        browse_button.setFixedWidth(100)
        self.layout.addWidget(output_dir_label, 1, 0)
        self.layout.addWidget(self.output_dir, 1, 1)
        self.layout.addWidget(browse_button, 1, 2)

        # add a small gap between the two sections
        self.layout.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum), 2, 0)

        # mde type (label) and radio button group
        mde_type_label = QLabel("MDE type")
        self.mde_type_data = QRadioButton("Data")
        self.mde_type_data.setObjectName("mde_type_data")
        self.mde_type_data.setChecked(True)
        self.mde_type_background_integrated = QRadioButton("Background (angle integrated)")
        self.mde_type_background_integrated.setObjectName("mde_type_background_integrated")
        self.mde_type_background_minimized = QRadioButton("Background (minimized by angle and energy)")
        self.mde_type_background_minimized.setObjectName("mde_type_background_minimized")
        # group the radio buttons to ensure mutually exclusive selection
        self.mde_type_button_group = QButtonGroup()
        self.mde_type_button_group.addButton(self.mde_type_data)
        self.mde_type_button_group.addButton(self.mde_type_background_integrated)
        self.mde_type_button_group.addButton(self.mde_type_background_minimized)
        self.layout.addWidget(mde_type_label, 3, 0)
        self.layout.addWidget(self.mde_type_data, 3, 1)
        self.layout.addWidget(self.mde_type_background_integrated, 4, 1)
        self.layout.addWidget(self.mde_type_background_minimized, 5, 1)

        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 6, 0)

        self.setLayout(self.layout)


class ReductionParameters(QGroupBox):
    """Generate reduction parameter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Reduction Parameters")


class Buttons(QWidget):
    """Processing buttons"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Generate"))
        layout.addWidget(QPushButton("Save settings"))
        layout.addStretch()
        self.setLayout(layout)
