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

        if ws_type == "mde":
            logger.information(f"Loading {filename} as MDE")
            load = AlgorithmManager.create("LoadMD")
        elif ws_type == "mdh":
            logger.information(f"Loading {filename} as MDH")
            load = AlgorithmManager.create("LoadMD")
        elif ws_type == "norm":
            logger.information(f"Loading {filename} as normalization")
            load = AlgorithmManager.create("LoadNexusProcessed")
        else:
            logger.error(f"Unsupported workspace type {ws_type} for {filename}")

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
            swn = load.getProperty("OutputWorkspace").value
            self.ads_observers.addHandle(swn, None)

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
        """Set the callback function for workspace changes"""
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

    def clearHandle(self):  # pylint: disable=invalid-name
        """Callback handle for ADS clear"""
        logger.debug("clearHandle")
        if self.callback:
            # NOTE: When closing the application, mantid will clear the ADS after
            #       Shiver is closed, which will cause a RuntimeError as widgets
            #       under shiver is no longer in scope.
            try:
                self.callback("clear", None, None)
            except RuntimeError:
                pass

    def addHandle(self, ws, _):  # pylint: disable=invalid-name
        """Callback handle for ADS add"""
        logger.debug(f"addHandle: {ws}")
        if self.callback:
            self.callback("add", ws, filter_ws(ws))

    def deleteHandle(self, ws, _):  # pylint: disable=invalid-name
        """Callback handle for ADS delete"""
        logger.debug(f"deleteHandle: {ws}")
        if self.callback:
            self.callback("del", ws, None)

    def replaceHandle(self, ws, _):  # pylint: disable=invalid-name
        """Callback handle for ADS replace"""
        logger.debug(f"replaceHandle: {ws}")
        if self.callback:
            self.callback("del", ws, None)
            self.callback("add", ws, filter_ws(ws))

    def renameHandle(self, old, new):  # pylint: disable=invalid-name
        """Callback handle for ADS rename"""
        logger.debug(f"renameHandle: {old} {new}")
        if self.callback:
            self.callback("del", old, None)
            self.callback("add", new, filter_ws(new))

    def register_call_back(self, callback):
        """Set the callback function for workspace changes"""
        self.callback = callback


def filter_ws(name):
    """Return the type of workspace"""
    ws_id = mtd[name].id()
    ws_type = None

    if ws_id == "MDHistoWorkspace":
        ws_type = "mdh"
    elif ws_id == "Workspace2D":
        # verify if it is one bin per histogram
        if mtd[name].blocksize() == 1:
            ws_type = "norm"
        else:
            logger.error(f"Workspace2D {name} has more than one bin per histogram")
    elif ws_id.startswith("MDEventWorkspace") and mtd[name].getNumDims() >= 4:
        # More detailed check
        mde_ws = mtd[name]
        dim_0 = mde_ws.getDimension(0).name
        dim_1 = mde_ws.getDimension(1).name
        dim_2 = mde_ws.getDimension(2).name
        dim_3 = mde_ws.getDimension(3).name
        # Last dimension must be momentum transfer, DeltaE
        # and the first 3 being either Q_sample or Q_lab
        if dim_3 == "DeltaE":
            if ("Q_sample" in dim_0) or ("Q_lab" in dim_0):
                if ("Q_sample" in dim_1) or ("Q_lab" in dim_1):
                    if ("Q_sample" in dim_2) or ("Q_lab" in dim_2):
                        ws_type = "mde"

    if ws_type is None:
        logger.error(f"Unsupported workspace type {ws_id} for {name}")

    return ws_type
