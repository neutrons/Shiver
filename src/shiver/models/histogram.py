"""Model for the Histogram tab"""
import os.path

# pylint: disable=no-name-in-module
from mantid.api import AlgorithmManager, AlgorithmObserver
from mantid.kernel import Logger
from mantid.geometry import SymmetryOperationFactory, SpaceGroupFactory, PointGroupFactory

logger = Logger("SHIVER")


class HistogramModel:
    """Histogram model"""

    def __init__(self):
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.error_callback = None

    def load(self, filename, ws_type):
        """Method to take filename and workspace type and load with correct algorithm"""
        ws_name, _ = os.path.splitext(os.path.basename(filename))

        if ws_type == "mde":
            logger.information(f"Loading {filename} as MDE")
            load = AlgorithmManager.create("LoadMD")
        elif ws_type == "norm":
            logger.information(f"Loading {filename} as normalization")
            load = AlgorithmManager.create("LoadNexusProcessed")
        else:
            logger.error(f"Unknown workspace type {ws_type} for {filename}")

        alg_obs = FileLoadingObserver(self, filename, ws_type)
        self.algorithms_observers.add(alg_obs)

        alg_obs.observeFinish(load)
        alg_obs.observeError(load)
        load.initialize()
        load.setLogging(False)
        try:
            load.setProperty("Filename", filename)
            load.setProperty("OutputWorkspace", ws_name)
            load.executeAsync()
        except ValueError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def finish_loading(self, obs, filename, ws_type, error=False, msg=""):  # pylint: disable=too-many-arguments
        """This is the callback from the algorithm observer"""
        if error:
            err_msg = f"Error loading {filename} as {ws_type}\n{msg}"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
        else:
            logger.information(f"Finished loading {filename}")
            self.algorithms_observers.remove(obs)

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def symmetry_operations(self, symmetry):
        """Validate the symmetry value with mandit"""
        if len(symmetry) != 0:          
            if (symmetry.isnumeric() and SpaceGroupFactory.isSubscribedNumber(int(symmetry))) or SpaceGroupFactory.isSubscribedSymbol(symmetry) or PointGroupFactory.isSubscribed(symmetry):
                # then it's valid
                logger.information(f"Symmetry {symmetry} is valid!")
            else:
                # check with SymmetryOperationFactory.createSymOps
                try:
                    SymmetryOperationFactory.createSymOps(symmetry)
                    logger.information(f"Symmetry {symmetry} is valid!")
                except RuntimeError as err:
                    err_msg = f"Invalid symmentry value: {symmetry}::{err} \n"
                    logger.error(err_msg)
                    if self.error_callback:
                        self.error_callback(err_msg)


class FileLoadingObserver(AlgorithmObserver):
    """Object to handle the execution events of the loading algorithms"""

    def __init__(self, parent, filename, ws_type):
        super().__init__()
        self.parent = parent
        self.filename = filename
        self.ws_type = ws_type

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call parent upon algorithm finishing"""
        self.parent.finish_loading(self, self.filename, self.ws_type)

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call parent upon algorithm error"""
        self.parent.finish_loading(self, self.filename, self.ws_type, True, msg)
