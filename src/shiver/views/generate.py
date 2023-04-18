"""PyQt widget for the histogram tab"""
import re
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
    QFileDialog,
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
        self.mde_type_widget = MDEType(self)
        layout.addWidget(self.mde_type_widget, 1, 2)
        layout.addWidget(ReductionParameters(self), 2, 2)

        self.buttons = Buttons(self)
        layout.addWidget(self.buttons, 1, 3, 2, 1)
        # connect to as_dict for user to see the dict before the saving
        # is fully implemented.
        self.buttons.save_btn.clicked.connect(self.mde_type_widget.as_dict)

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

        # cached values
        self._mde_name = None
        self._output_dir = None

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
        # connect the browse button to the browse function
        browse_button.clicked.connect(self._browse)

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

    def _browse(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select output directory")
        if directory != self._output_dir:
            self._output_dir = directory
            self.output_dir.setText(directory)

    def check_mde_name(self) -> bool:
        """Check if the mde name is valid.

        Returns:
        --------
            bool: True if the mde name is valid, False otherwise.
        """
        mde_name = self.mde_name.text()

        if is_valid_name(mde_name):
            self._mde_name = mde_name
            return True

        return False

    def check_output_dir(self) -> bool:
        """Check if the output directory is valid.

        Returns:
        --------
        bool:
            True if the output directory is not empty and does not contains any
            special char, False otherwise.
        """
        output_dir = self.output_dir.text()

        if output_dir == "":
            return False

        if has_special_char(output_dir):
            return False

        self._output_dir = output_dir
        return True

    @property
    def is_valid(self) -> bool:
        """Check if the MDE type widget is valid."""
        return self.check_mde_name() and self.check_output_dir()

    def as_dict(self) -> dict:
        """Return the MDE type widget as a dictionary."""
        if self.is_valid:
            rst = {
                "mde_name": self._mde_name,
                "output_dir": self._output_dir,
                "mde_type": self.mde_type_button_group.checkedButton().text(),
            }
        else:
            rst = {}

        print(rst)
        return rst


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
        self.generate_btn = QPushButton("Generate")
        layout.addWidget(self.generate_btn)
        self.save_btn = QPushButton("Save settings")
        layout.addWidget(self.save_btn)
        layout.addStretch()
        self.setLayout(layout)


def is_valid_name(var_name: str) -> bool:
    """Check if the variable name is valid.

    Parameters:
    -----------
    var_name: str
        The variable name to check.

    Returns:
    --------
    bool:
        True if the variable name is valid, False otherwise.

    NOTE:
    -----
        The variable name must follow the following rules:
        - must not be empty
        - must start with a letter or underscore
        - must only contain letters, numbers, and underscores
    """
    if not var_name:
        return False
    if not var_name[0].isalpha() and var_name[0] != "_":
        return False
    for char in var_name:
        if not char.isalnum() and char != "_":
            return False
    return True


def has_special_char(var_name: str) -> bool:
    """Check if the variable name contains special characters.

    Parameters:
    -----------
    var_name: str
        The variable name to check.

    Returns:
    --------
    bool:
        True if the variable name contains special characters, False otherwise.
    """
    regex = re.compile("[@!#$%^&*()<>?|}{~]")
    return regex.search(var_name) is not None
