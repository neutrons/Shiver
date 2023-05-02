"""PyQt widget for the histogram tab"""
import re
import itertools
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
    QErrorMessage,
)
from qtpy.QtCore import Signal
from .data import RawData
from .oncat import Oncat


class Generate(QWidget):
    """Generate widget"""

    error_message_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        layout.setRowMinimumHeight(1, 200)
        layout.setRowMinimumHeight(2, 200)
        layout.setColumnMinimumWidth(1, 400)
        layout.setColumnMinimumWidth(2, 400)
        layout.setColumnMinimumWidth(3, 400)

        # Raw data widget
        self.raw_data_widget = RawData(self)
        layout.addWidget(self.raw_data_widget, 1, 1)

        # Oncat widget
        self.oncat_widget = Oncat(self)
        layout.addWidget(self.oncat_widget, 2, 1)
        self.oncat_widget.connect_error_callback(self.show_error_message)

        # MDE type widget
        self.mde_type_widget = MDEType(self)
        layout.addWidget(self.mde_type_widget, 1, 2)
        self.mde_type_widget.connect_error_callback(self.show_error_message)
        self.mde_type_widget.connect_update_title_callback(self._update_title)

        # Reduction parameters widget
        layout.addWidget(ReductionParameters(self), 2, 2)

        # Buttons widget
        self.buttons = Buttons(self)
        layout.addWidget(self.buttons, 1, 3, 2, 1)
        # connect to as_dict for user to see the dict before the saving
        # is fully implemented.
        self.buttons.save_btn.clicked.connect(self.as_dict)

        self.setLayout(layout)

        # Error message handling
        self.error_message_signal.connect(self._show_error_message)

        # Cross widget connections
        # - update of instrument in oncat widget should update the path in
        #   the raw data widget if oncat is connected.
        self.oncat_widget.instrument.currentTextChanged.connect(self.update_raw_data_widget_path)
        # - update of IPTS in oncat widget should update the path in the raw
        #   data widget if oncat is connected.
        self.oncat_widget.ipts.currentTextChanged.connect(self.update_raw_data_widget_path)
        # - update of selected datasets in oncat widget should update the selection
        #   in the raw data widget if oncat is connected.
        self.oncat_widget.dataset.currentTextChanged.connect(self.update_raw_data_widget_selection)
        # - change the dataset to "custom" if the selection in the raw data widget
        #   is changed.
        self.raw_data_widget.files.itemSelectionChanged.connect(self.oncat_widget.set_dataset_to_custom)

    def update_raw_data_widget_path(self):
        """Update the path in the raw data widget"""
        if self.oncat_widget.connected_to_oncat:
            suggested_path = self.oncat_widget.get_suggested_path()
            self.raw_data_widget.path.setText(suggested_path)

    def update_raw_data_widget_selection(self):
        """Update the selection in the raw data widget"""
        if self.oncat_widget.connected_to_oncat:
            suggested_selected_files = self.oncat_widget.get_suggested_selected_files()
            if suggested_selected_files:
                # flatten the list and remove duplicates
                suggested_selected_files = list(itertools.chain(*suggested_selected_files))
                self.raw_data_widget.set_selected(suggested_selected_files)

    def _update_title(self, mde_name: str):
        """Update the title of the widget to include the MDE name"""
        tab_widget = self.parent().parent()
        tab_widget.setTabText(
            tab_widget.currentIndex(),
            f"Generate - {mde_name}",
        )

    def as_dict(self) -> dict:
        """Return the widget as a dict.

        Returns
        -------
        dict
            The widget as a dict.
        """
        rst = {}
        # add diction content from MDE type widget
        rst.update(self.mde_type_widget.as_dict())
        # other widgets to be added here

        # NOTE: during development, print the dict to the console
        print(rst)
        return rst

    def populate_from_dict(self, data: dict):
        """Populate all child widgets with the given dict.

        Parameters
        ----------
        data : dict
            The data to populate the widgets with.
        """
        self.mde_type_widget.populate_from_dict(data)

    def show_error_message(self, msg):
        """Will show a error dialog with the given message

        This will emit a signal so that other threads can call this but have the GUI thread execute"""
        self.error_message_signal.emit(msg)

    def _show_error_message(self, msg):
        """Will show a error dialog with the given message from qt signal"""
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()


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
        # connect the mde name input to the update title function
        self.mde_name.textChanged.connect(self._update_title)

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

        self.update_title_callback = None
        self.error_callback = None

    def _browse(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select output directory")
        if directory != self._output_dir:
            self._output_dir = directory
            self.output_dir.setText(directory)

    def _update_title(self):
        """Update the title of the parent widget based on the mde name."""
        if self.update_title_callback:
            self.update_title_callback(self.mde_name.text().strip())

    def check_mde_name(self) -> bool:
        """Check if the mde name is valid.

        Returns:
        --------
            bool: True if the mde name is valid, False otherwise.
        """
        mde_name = self.mde_name.text().strip()

        if is_valid_name(mde_name):
            self._mde_name = mde_name
            return True

        # the name is not valid
        if self.error_callback:
            self.error_callback("Invalid MDE name.")

        # empty the mde name
        self.mde_name.setText("")

        return False

    def check_output_dir(self) -> bool:
        """Check if the output directory is valid.

        Returns:
        --------
        bool:
            True if the output directory is not empty and does not contains any
            special char, False otherwise.
        """
        output_dir = self.output_dir.text().strip()

        if output_dir == "":
            if self.error_callback:
                self.error_callback("Output directory cannot be empty.")
            return False

        if has_special_char(output_dir):
            if self.error_callback:
                self.error_callback("Output directory cannot contain special characters.")
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

        return rst

    def populate_from_dict(self, param_dict: dict) -> bool:
        """Populate the MDE type widget from a dictionary.

        Parameters:
        -----------
        param_dict: dict
            The dictionary containing the MDE type widget parameters.

        Returns:
        --------
        bool:
            True if the MDE type widget is populated successfully, False otherwise.
        """
        mde_name = param_dict.get("mde_name", "")
        output_dir = param_dict.get("output_dir", "")
        mde_type = param_dict.get("mde_type", "")

        # sanity check before assigning values
        # mde name must be valid
        if not is_valid_name(mde_name):
            if self.error_callback:
                self.error_callback("Invalid MDE name found in history.")
            return False
        # output directory must be valid
        if output_dir == "" or has_special_char(output_dir):
            if self.error_callback:
                self.error_callback("Invalid output directory found in history.")
            return False
        # mde type must be valid
        if mde_type not in ["Data", "Background (angle integrated)", "Background (minimized by angle and energy)"]:
            if self.error_callback:
                self.error_callback("Invalid MDE type found in history.")
            return False

        # assign values
        self.mde_name.setText(mde_name)
        self.output_dir.setText(output_dir)
        if mde_type == "Data":
            self.mde_type_data.setChecked(True)
        elif mde_type == "Background (angle integrated)":
            self.mde_type_background_integrated.setChecked(True)
        elif mde_type == "Background (minimized by angle and energy)":
            self.mde_type_background_minimized.setChecked(True)
        else:
            # this should never happen
            raise RuntimeError("Invalid MDE type found in history.")

        return True

    def connect_update_title_callback(self, callback):
        """Connect the update title callback.

        Parameters:
        -----------
        callback: callable
            The update title callback.
        """
        self.update_title_callback = callback

    def connect_error_callback(self, callback):
        """Connect the error callback.

        Parameters:
        -----------
        callback: callable
            The error callback.
        """
        self.error_callback = callback

    def re_init_widget(self):
        """Re-initialize the widget."""
        self.mde_name.setText("")
        self.output_dir.setText("")
        self.mde_type_data.setChecked(True)


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
        self.save_btn = QPushButton("Save configuration")
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
