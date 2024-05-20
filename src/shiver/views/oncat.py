"""PyQt widget for the OnCat widget in General tab."""

import os
import json
import oauthlib
import numpy as np
import pyoncat
from pyoncatqt.login import ONCatLogin
from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QComboBox,
    QDialog,
    QLineEdit,
    QDoubleSpinBox,
)
from qtpy.QtCore import QTimer
from shiver.configuration import get_data


class OncatToken:
    """Class to hold OnCat token"""

    def __init__(self, token_path: str):
        self.token_path = token_path

    def read_token(self):
        """Read token from file"""
        # If there is not a token stored, return
        # None from the callback.
        if not os.path.exists(self.token_path):
            return None

        with open(self.token_path, encoding="UTF-8") as storage:
            return json.load(storage)

    def write_token(self, token):
        """Write token to file"""
        # check if directory exists
        if not os.path.exists(os.path.dirname(self.token_path)):
            os.makedirs(os.path.dirname(self.token_path))
        # write token to file
        with open(self.token_path, "w", encoding="UTF-8") as storage:
            json.dump(token, storage)
        # change permissions to read-only by user
        os.chmod(self.token_path, 0o600)


class OnCatAgent:
    """Agent to interface with OnCat"""

    def __init__(self, use_notes=False) -> None:
        """Initialize OnCat agent"""
        # get configuration settings
        self._use_notes = use_notes
        self._oncat_url = get_data("generate_tab.oncat", "oncat_url")
        self._client_id = get_data("generate_tab.oncat", "client_id")

        user_home_dir = os.path.expanduser("~")
        self._token = OncatToken(
            os.path.abspath(f"{user_home_dir}/.shiver/oncat_token.json"),
        )
        self._agent = pyoncat.ONCat(
            self._oncat_url,
            client_id=self._client_id,
            # Pass in token getter/setter callbacks here:
            token_getter=self._token.read_token,
            token_setter=self._token.write_token,
            flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW,
        )

    def login(self, username: str, password: str):
        """Connect to OnCat with given username and password.

        Parameters
        ----------
        username : str
            Username for OnCat
        password : str
            Password for OnCat
        """
        self._agent.login(username, password)

    @property
    def has_token(self):
        """Check if token exists"""
        return self._token.read_token() is not None

    @property
    def is_connected(self):
        """Check if connected to OnCat"""
        try:
            self._agent.Facility.list()  # pylint: disable=no-member
            return True
        except pyoncat.InvalidRefreshTokenError:
            return False
        except pyoncat.LoginRequiredError:
            return False
        except Exception:  # pylint: disable=W0718
            return False

    def get_ipts(self, facility: str, instrument: str) -> list:
        """Get IPTS numbers for given facility and instrument.

        Parameters
        ----------
        facility : str
            Facility name
        instrument : str
            Instrument name

        Returns
        -------
        list
            List of IPTS numbers in string format (IPTS-XXXXX)
        """
        # return empty list if not connected
        if not self.is_connected:
            return []
        # get list of experiments
        experiments = self._agent.Experiment.list(  # pylint: disable=no-member
            facility=facility,
            instrument=instrument,
            projection=["facility", "instrument"],
        )
        return list({exp["id"] for exp in experiments})

    def get_datasets(self, facility: str, instrument: str, ipts: int) -> list:
        """Get datasets for given facility, instrument, and IPTS.

        Parameters
        ----------
        facility : str
            Facility name
        instrument : str
            Instrument name
        ipts : int
            IPTS number

        Returns
        -------
        list
            List of datasets
        """
        # return empty list if not connected
        if not self.is_connected:
            return []
        # get list of datasets
        return get_dataset_names(
            self._agent,
            ipts_number=ipts,
            instrument=instrument,
            use_notes=self._use_notes,
            facility=facility,
        )

    def get_agent_instance(self):
        """Get OnCat agent instance"""
        return self._agent


class OnCatLogin(QDialog):
    """OnCat login dialog"""

    def __init__(self, parent=None, error_message_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Use U/XCAM to connect to OnCat")
        self.resize(350, 200)
        layout = QGridLayout()
        label1 = QLabel("UserId")
        self.user_obj = QLineEdit()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.user_obj, 0, 1)
        label2 = QLabel("Password")
        self.user_pwd = QLineEdit()
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.user_pwd, 1, 1)
        self.user_pwd.setEchoMode(QLineEdit.Password)
        self.button_login = QPushButton("Login")
        layout.addWidget(self.button_login, 2, 0, 2, 2)
        self.setLayout(layout)

        # connect signals and slots
        self.button_login.clicked.connect(self.accept)

        self.error_message_callback = error_message_callback

    def accept(self):
        """Accept"""
        # login to OnCat
        try:
            self.parent().oncat_agent.login(
                self.user_obj.text(),
                self.user_pwd.text(),
            )
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            if self.error_message_callback is not None:
                self.error_message_callback(
                    "Invalid username or password. Please try again.",
                )
            self.user_pwd.setText("")
            return
        except pyoncat.LoginRequiredError:
            if self.error_message_callback is not None:
                self.error_message_callback(
                    "A username and/or password was not provided when logging in.",
                )
            self.user_pwd.setText("")
            return

        # ask parent to sync
        self.parent().sync_with_remote()
        # close dialog
        self.close()


class Oncat(QGroupBox):
    """ONCat widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # layout for options
        self.setTitle("ONCat")
        self.oncat_options_layout = QGridLayout()
        # dropdown list for instrument
        self.instrument_label = QLabel("Instrument")
        self.instrument = QComboBox()
        self.instrument.setToolTip("Direct geometry instruments available in ONCat.")
        self.instrument_items = ["ARCS", "CNCS", "HYSPEC", "SEQUOIA"]
        self.instrument.addItems(self.instrument_items)
        self.oncat_options_layout.addWidget(self.instrument_label, 0, 0)
        self.oncat_options_layout.addWidget(self.instrument, 0, 1)
        # dropdown list for IPTS
        self.ipts_label = QLabel("IPTS")
        self.ipts = QComboBox()
        self.ipts.setToolTip("List of experiments available on ONCat for the given instrument.")
        self.ipts_items = []
        self.ipts.addItems(self.ipts_items)
        self.oncat_options_layout.addWidget(self.ipts_label, 1, 0)
        self.oncat_options_layout.addWidget(self.ipts, 1, 1)
        # dropdown list for dataset
        self.dataset_label = QLabel("Select dataset")
        self.dataset = QComboBox()
        self.dataset.setToolTip("List of named datasets in the current IPTS.")
        self.dataset_items = ["custom"]
        self.dataset.addItems(self.dataset_items)
        self.oncat_options_layout.addWidget(self.dataset_label, 2, 0)
        self.oncat_options_layout.addWidget(self.dataset, 2, 1)
        # dropdown list for angle integration target
        self.angle_target_label = QLabel("Angle integration step")
        self.angle_target = QDoubleSpinBox()
        self.angle_target.setToolTip("Files within this angle range will be added together, to reduce memory usage.")
        self.angle_target.setRange(0, 360)
        # default to 1: 1 degree
        self.angle_target.setValue(0.1)
        self.oncat_options_layout.addWidget(self.angle_target_label, 3, 0)
        self.oncat_options_layout.addWidget(self.angle_target, 3, 1)

        # status indicator (disconnected: red, connected: green)
        self.status_label = QLabel("")
        self.status_label.setToolTip("ONCat connection status.")
        self.oncat_options_layout.addWidget(self.status_label, 4, 0)

        # connect to OnCat button
        self.oncat_button = QPushButton("&Connect to ONCat")
        self.oncat_button.setFixedWidth(300)
        self.oncat_button.setToolTip("Connect to ONCat (requires login credentials).")
        self.oncat_options_layout.addWidget(self.oncat_button, 4, 1)

        self.second_oncat = ONCatLogin(parent=self, key="shiver")
        self.second_oncat.connection_updated.connect(self.update_status)
        self.oncat_options_layout.addWidget(self.second_oncat, 5, 0, 1, 2)

        # set layout
        self.setLayout(self.oncat_options_layout)

        # connect signals and slots
        self.oncat_button.clicked.connect(self.connect_to_oncat)

        # error message callback
        self.error_message_callback = None

        self.use_notes = get_data("generate_tab.oncat", "use_notes")
        # OnCat agent
        self.oncat_agent = OnCatAgent(self.use_notes)

        # Sync with remote
        self.sync_with_remote(refresh=True)

        # Sync with remote every 60 seconds
        # NOTE: make the refresh interval configurable
        #       in application settings
        self.update_connection_status_timer = QTimer()
        self.update_connection_status_timer.timeout.connect(
            self.sync_with_remote,
        )
        self.update_connection_status_timer.start(60_000)

        # change in instrument should trigger update of
        # - IPTS
        # - dataset
        self.instrument.currentTextChanged.connect(self.update_ipts)
        self.instrument.currentTextChanged.connect(self.update_datasets)

        # change in IPTS should trigger update of
        # - dataset
        self.ipts.currentTextChanged.connect(self.update_datasets)

    @property
    def connected_to_oncat(self) -> bool:
        """Check if connected to OnCat"""
        return self.oncat_agent.is_connected

    def get_suggested_path(self) -> str:
        """Return a suggested path based on current selection."""
        return os.path.join(
            "/",
            self.get_facility(),
            self.get_instrument(),
            self.get_ipts(),
            "nexus",
        )

    def update_status(self):
        """Update connection status"""
        self.sync_with_remote(refresh=True)

    def get_suggested_selected_files(self) -> list:
        """Return a list of suggested files to be selected based on dataset selection."""
        if self.get_dataset() in (" ", "custom"):
            return []  # no suggestion to make

        group_by_angle = self.angle_target.value() > 0

        return get_dataset_info(
            login=self.oncat_agent.get_agent_instance(),
            ipts_number=self.get_ipts_number(),
            instrument=self.get_instrument(),
            use_notes=self.use_notes,
            facility=self.get_facility(),
            group_by_angle=group_by_angle,
            angle_bin=self.angle_target.value(),
            dataset_name=self.get_dataset(),
        )

    def set_dataset_to_custom(self):
        """Set dataset to custom"""
        self.dataset.setCurrentIndex(self.dataset.findText("custom"))

    def connect_to_oncat(self):
        """Connect to OnCat"""
        # check if connection exists
        if self.connected_to_oncat:
            return

        # check if token exists
        if self.oncat_agent.has_token:
            if self.error_message_callback:
                self.error_message_callback("Session expired. Please login again.")

        # prompt for username and password
        oncat_login = OnCatLogin(self, self.error_message_callback)
        oncat_login.show()

        # update connection status
        self.sync_with_remote(refresh=True)

    def sync_with_remote(self, refresh=False):
        """Update all items within OnCat widget."""
        self.update_connection_status()

        if self.connected_to_oncat and refresh:
            self.update_ipts()
            self.update_datasets()

    def update_connection_status(self):
        """Update connection status"""
        if self.oncat_agent.is_connected:
            self.status_label.setText("ONCat: Connected")
            self.status_label.setStyleSheet("color: green")
        else:
            self.status_label.setText("ONCat: Disconnected")
            self.status_label.setStyleSheet("color: red")

    def connect_error_callback(self, callback):
        """Connect error message callback"""
        self.error_message_callback = callback

    def as_dict(self) -> dict:
        """Return widget state as dictionary"""
        return {
            "instrument": self.instrument.currentText(),
            "ipts": self.ipts.currentText(),
            "dataset": self.dataset.currentText(),
            "angle_target": self.angle_target.value(),
        }

    def populate_from_dict(self, state: dict):
        """Populate widget from dictionary"""
        self.instrument.setCurrentText(state["instrument"])
        self.ipts.setCurrentText(state["ipts"])
        self.dataset.setCurrentText(state["dataset"])
        self.angle_target.setValue(state["angle_target"])

    def get_angle_integration(self):
        """Get angle integration target"""
        return self.angle_target.value()

    def get_dataset(self):
        """Get dataset"""
        return self.dataset.currentText()

    def get_ipts(self):
        """Get IPTS"""
        return self.ipts.currentText()

    def get_ipts_number(self):
        """Get IPTS number"""
        if self.get_ipts() == "":
            return None

        return int(self.get_ipts().split("-")[1])

    def get_instrument(self):
        """Get instrument"""
        instrument = self.instrument.currentText()
        # NOTE: HYSEPC is stored as HYS on OnCat
        if instrument == "HYSPEC":
            instrument = "HYS"
        # NOTE: SEQUOIA is stored as SEQ on OnCat
        if instrument == "SEQUOIA":
            instrument = "SEQ"
        return instrument

    def get_facility(self):
        """Get facility based on instrument"""
        return {"ARCS": "SNS", "CNCS": "SNS", "HYS": "SNS", "SEQ": "SNS"}[self.get_instrument()]

    def update_ipts(self):
        """Update IPTS list"""
        # get IPTS list from OnCat
        ipts_list = self.oncat_agent.get_ipts(
            self.get_facility(),
            self.get_instrument(),
        )
        # update IPTS list
        self.ipts.clear()
        self.ipts.addItems(sorted(ipts_list, key=lambda x: int(x.split("-")[1])))

    def update_datasets(self):
        """Update dataset list"""
        # get dataset list from OnCat
        dataset_list = ["custom"] + self.oncat_agent.get_datasets(
            self.get_facility(),
            self.get_instrument(),
            self.get_ipts_number(),
        )
        # update dataset list
        self.dataset.clear()
        self.dataset.addItems(sorted(dataset_list))


# The following are utility functions migrated from the original
# oncat_util.py
def get_data_from_oncat(
    login: pyoncat.ONCat,
    projection: list,
    ipts_number: int,
    instrument: str,
    facility: str = "SNS",
    tags: str = "type/raw",
) -> dict:
    """
    Get data according to a projection from oncat

    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database.
    projection : list
        A list of paths in the oncat datafile to extract the relevant information.
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')
    tags : str, optional
        The type of files to look for in the OnCat database (Default = 'type/raw')

    Returns:
    --------
    datafiles: dict
        A dictionary containing information requested from the OnCat database
    """
    datafiles = login.Datafile.list(
        facility=facility,
        instrument=instrument,
        experiment=f"IPTS-{ipts_number}",
        projection=projection,
        tags=tags,
    )
    return datafiles


def get_dataset_names(
    login: pyoncat.ONCat,
    ipts_number: int,
    instrument: str,
    use_notes: bool = False,
    facility: str = "SNS",
) -> list:
    """
    A function to return the names of the datasets, either from sequence names or from comments

    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database.
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    use_notes : bool, optional
        A flag to indicate that the names of the datasets are stored in the
        Notes/Comments (as opposed to sequence name)
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')

    Returns:
    --------
    dsn: set of strings
        A set containing strings with the dataset names, as tored in the OnCat database
    """
    projection = ["metadata.entry.daslogs.sequencename", "metadata.entry.notes"]
    datasets = get_data_from_oncat(login, projection, ipts_number, instrument, facility)

    try:
        if use_notes:
            dsn = [datasets[i]["metadata"]["entry"].get("notes", None) for i in range(len(datasets))]
        else:
            dsn = [
                datasets[i]["metadata"]["entry"].get("daslogs", {}).get("sequencename", {}).get("value", None)
                for i in range(len(datasets))
            ]
    except (KeyError, TypeError):
        # if keys do not exist following the expected schema return an empty list dsn = []
        dsn = []
        return dsn
    # remove None values
    dsn = [ds for ds in dsn if ds is not None]

    # deal with more than one sequence name
    dsn = [ds if isinstance(ds, str) else ds[-1] for ds in dsn]
    dsn = list(set(dsn))
    return dsn


def get_dataset_info(  # pylint: disable=too-many-branches
    *,
    login,
    ipts_number,
    instrument,
    dataset_name=None,
    use_notes=False,
    facility="SNS",
    group_by_angle=False,
    angle_pv="omega",
    angle_bin=0.5,
    include_runs=None,
    exclude_runs=None,
):
    """
    A function to return a list of runs in a dataset, optionally grouped by angle.
    Grouping by angle is from the lowest value, within angle_bin.

    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database.
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    dataset_name : str, optional
        The name of a dataset to look for in the database. It can be None.
    use_notes : bool, optional
        A flag to indicate that the names of the datasets are stored in the
        Notes/Comments (as opposed to sequence name)
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')
    group_by_angle : bool, optional
        A flag to indicate if the runs should be grouped by angle
    angle_pv : str, optional
        The name of the angle process variable. The value read from this variable
        will be used for grouping files together.Default is 'omega'
    angle_bin : float, optional
        The maximum difference (in degrees) between angles in the same group. Default is 0.5
    include_runs : array_like, optional
        A list or array of additional runs to be added to the same dataset. The default is None
    exclude_runs : array_like, optional
        A list or array of runs to be excluded from the dataset. The default is None

    Returns:
    --------
    file_names : list
        List of runs in the dataset, or list of list of runs at the same angle

    Raises:
    -------
    ValueError
        If any of the include_runs is not in the OnCat database for this IPTS
        If any of the include_runs is already in the dataset
        If any of the exclude_runs is not already accounted for
        If no runs were found to match the criteria (for example,
        dataset_name=None and include_runs=None)
    """
    # get run number, angle, and sequence names from oncat
    projection = ["indexed.run_number", f"metadata.entry.daslogs.{angle_pv}"]
    if use_notes:
        projection.append("metadata.entry.notes")
    else:
        projection.append("metadata.entry.daslogs.sequencename")
    datafiles = get_data_from_oncat(login, projection, ipts_number, instrument, facility)

    # {"run_num": "locations"}
    lookup_table = {df["indexed"]["run_number"]: df["location"] for df in datafiles}

    run_number = np.empty(len(datafiles), dtype="int")
    angle = {}
    sequence = np.empty(len(datafiles), dtype="U50")
    for idx, datafile in enumerate(datafiles):
        run_number[idx] = datafile["indexed"]["run_number"]
        angle[str(run_number[idx])] = (
            datafile["metadata"]["entry"].get("daslogs", {}).get(angle_pv, {}).get("average_value", np.NaN)
        )
        if use_notes:
            sid = datafile["metadata"]["entry"].get("notes", None)
        else:
            sid = datafile["metadata"]["entry"].get("daslogs", {}).get("sequencename", {}).get("value", np.NaN)
        if isinstance(sid, list):
            sid = sid[-1]
        sequence[idx] = sid
    if dataset_name:
        good_runs = run_number[sequence == dataset_name]
    else:
        good_runs = np.array([], dtype="int")

    # include runs
    if include_runs:
        include_runs = np.array(include_runs)
        # check if all include_runs are part of this IPTS
        condition = np.in1d(include_runs, run_number)
        if not np.all(condition):
            not_found = include_runs[np.logical_not(condition)]
            bad_str = ", ".join([str(nf) for nf in not_found])
            raise ValueError(f"Could not find the following 'include_runs' in this IPTS: {bad_str}")
        # check if runs already in the good_runs
        condition = np.in1d(include_runs, good_runs)
        if np.any(condition):
            already_there = include_runs[condition]
            bad_str = ", ".join([str(at) for at in already_there])
            raise ValueError(f"The following 'include_runs' are already part of the dataset: {bad_str}")
        good_runs = np.append(good_runs, include_runs)

    # exclude runs
    if exclude_runs:
        exclude_runs = np.array(exclude_runs)
        # check if all the exclude_runs are already selected
        condition = np.in1d(exclude_runs, good_runs)
        if not np.all(condition):
            not_found = exclude_runs[np.logical_not(condition)]
            bad_str = ", ".join([str(nf) for nf in not_found])
            raise ValueError(f"The following 'exclude_runs' are not in this dataset: {bad_str}")
        good_runs = good_runs[np.in1d(good_runs, exclude_runs, invert=True)]

    # no runs found
    if len(good_runs) == 0:
        return []
        # raise ValueError("Could not find any runs matching your criteria")

    # group by angle if desired
    if group_by_angle:
        angle_list = [angle[str(r)] for r in good_runs]
        # sort runs by angle
        tmp = list(sorted(zip(angle_list, good_runs)))
        angle_list, good_runs = zip(*tmp)
        angle_list = np.array(angle_list)
        good_runs = np.array(good_runs)
        grouped_runs = []
        grouped_filenames = []
        while len(good_runs) > 0:
            inds = angle_list - angle_list[0] < angle_bin
            grouped_runs.append(good_runs[inds].tolist())
            grouped_filenames.append([lookup_table[r] for r in good_runs[inds]])

            good_runs = good_runs[np.logical_not(inds)]
            angle_list = angle_list[np.logical_not(inds)]

        good_runs = grouped_runs
        filenames = grouped_filenames
    else:
        good_runs = good_runs.tolist()
        filenames = [lookup_table[r] for r in good_runs]

    return filenames
