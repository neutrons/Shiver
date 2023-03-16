"""Model for the Histogram tab"""
import os.path

# pylint: disable=no-name-in-module
from mantid.api import AlgorithmManager, AlgorithmObserver, AnalysisDataServiceObserver
from mantid.simpleapi import mtd
from mantid.kernel import Logger

logger = Logger("SHIVER")


class HistogramModel:
    """Histogram model"""

    def __init__(self):
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.ads_observers = ADSObserver()
        self.error_callback = None

    def load(self, filename, ws_type):
        """Method to take filename and workspace type and load with correct algorithm"""
        ws_name, _ = os.path.splitext(os.path.basename(filename))

        # Check if the workspace already exists
        if mtd.doesExist(ws_name):
            logger.warning(f"Workspace {ws_name} already exists")
            return

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

        if load.isExecuted():
            self.ads_observers.addHandle(ws_name, None)

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

    def ws_change_call_back(self, callback):
        self.ads_observers.register_call_back(callback)


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


class ADSObserver(AnalysisDataServiceObserver):
    """Object to handle interactions with the ADS"""

    def __init__(self):
        super().__init__()
        self.observeClear(True)
        self.observeAdd(True)
        self.observeDelete(True)
        self.observeReplace(True)
        self.observeRename(True)
        self.callback = None

    def clearHandle(self):
        logger.debug("clearHandle")
        if self.callback:
            # NOTE: When closing the application, mantid will clear the ADS after
            #       Shiver is closed, which will cause a RuntimeError as widgets
            #       under shiver is no longer in scope.
            try:
                self.callback("clear", None, None)
            except RuntimeError:
                pass

    def addHandle(self, ws, _):
        logger.debug(f"addHandle: {ws}")
        if self.callback:
            self.callback("add", ws, filter_ws(ws))

    def deleteHandle(self, ws, _):
        logger.debug(f"deleteHandle: {ws}")
        if self.callback:
            self.callback("del", ws, None)
        self.del_ws(ws)

    def replaceHandle(self, ws, _):
        logger.debug(f"replaceHandle: {ws}")
        if self.callback:
            self.callback("del", ws, None)
            self.callback("add", ws, filter_ws(ws))

    def renameHandle(self, old, new):
        logger.debug(f"renameHandle: {old} {new}")
        if self.callback:
            self.callback("del", old, None)
            self.callback("add", new, filter_ws(new))

    def register_call_back(self, callback):
        self.callback = callback


def filter_ws(name):
    if mtd[name].isMDHistoWorkspace():
        return "mde"
    else:
        return "norm"
