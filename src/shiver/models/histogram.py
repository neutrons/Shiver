"""Model for the Histogram tab"""
import os.path

# pylint: disable=no-name-in-module
from mantid.api import AlgorithmManager, AlgorithmObserver, AnalysisDataServiceObserver
from mantid.simpleapi import mtd, DeleteWorkspace, RenameWorkspace, SaveMD
from mantid.kernel import Logger
from mantid.geometry import (
    SymmetryOperationFactory,
    SpaceGroupFactory,
    PointGroupFactory,
)

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

        alg_obs = FileLoadingObserver(self, filename, ws_type, ws_name)
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

    def delete(self, ws_name):
        """Delete the workspace"""
        DeleteWorkspace(ws_name)

    def rename(self, old_name, new_name):
        """Rename the workspace from old_name to new_name"""
        RenameWorkspace(old_name, new_name)

    def save(self, ws_name, filename):
        """Save the workspace"""
        SaveMD(ws_name, filename)

    def save_history(self, ws_name, filename):
        """Save the mantid algorithm history"""
        history = mtd[ws_name].getHistory()

        script = [f"from mantid.simpleapi import {', '.join(alg.name() for alg in history.getAlgorithmHistories())}"]

        for alg in history.getAlgorithmHistories():
            script.append(
                "{}({})".format(  # pylint: disable=consider-using-f-string
                    alg.name(),
                    ", ".join(
                        f"{p.name()}='{alg.getPropertyValue(p.name())}'"
                        for p in alg.getProperties()
                        if alg.getPropertyValue(p.name())
                    ),
                )
            )

        with open(filename, "w", encoding="utf-8") as f_open:
            f_open.write("\n".join(script))

    def finish_loading(self, obs, filename, ws_type, ws_name, error=False, msg=""):
        """This is the callback from the algorithm observer"""
        if error:
            err_msg = f"Error loading {filename} as {ws_type}\n{msg}"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
        else:
            if ws_type != filter_ws(ws_name):
                err_msg = f"File {filename} doesn't match type required, deleting workspace {ws_name}"
                logger.error(err_msg)
                if self.error_callback:
                    self.error_callback(err_msg)
                DeleteWorkspace(ws_name)
            else:
                logger.information(f"Finished loading {filename}")

            self.algorithms_observers.remove(obs)

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def symmetry_operations(self, symmetry):
        """Validate the symmetry value with mantid"""
        if len(symmetry) != 0:
            if (
                (symmetry.isnumeric() and SpaceGroupFactory.isSubscribedNumber(int(symmetry)))
                or SpaceGroupFactory.isSubscribedSymbol(symmetry)
                or PointGroupFactory.isSubscribed(symmetry)
            ):
                # then it's valid
                logger.information(f"Symmetry {symmetry} is valid!")
            else:
                # check with SymmetryOperationFactory.createSymOps
                try:
                    SymmetryOperationFactory.createSymOps(symmetry)
                    logger.information(f"Symmetry {symmetry} is valid!")
                except RuntimeError as err:
                    err_msg = f"Invalid symmetry value: {symmetry}::{err} \n"
                    logger.error(err_msg)
                    if self.error_callback:
                        self.error_callback(err_msg)

    def ws_change_call_back(self, callback):
        """Set the callback function for workspace changes"""
        self.ads_observers.register_call_back(callback)

    def get_all_valid_workspaces(self):
        """Get all existing workspaces"""
        return ((name, filter_ws(name), get_frame(name)) for name in mtd.getObjectNames() if filter_ws(name))

    def do_make_slice(self, config: dict):
        """Method to take filename and workspace type and load with correct algorithm"""
        alg = AlgorithmManager.create("MakeSlice")
        alg_obs = MakeSliceObserver(parent=self)
        self.algorithms_observers.add(alg_obs)

        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)
        alg.initialize()
        alg.setLogging(False)
        try:
            alg.setProperty("InputWorkspace", config.get("InputWorkspace"))
            alg.setProperty("BackgroundWorkspace", config.get("BackgroundWorkspace", None))
            alg.setProperty(
                "NormalizationWorkspace",
                config.get("NormalizationWorkspace", None),
            )
            alg.setProperty("QDimension0", config.get("QDimension0"))
            alg.setProperty("QDimension1", config.get("QDimension1"))
            alg.setProperty("QDimension2", config.get("QDimension2"))
            alg.setProperty("Dimension0Name", config.get("Dimension0Name"))
            alg.setProperty("Dimension0Binning", config.get("Dimension0Binning", ""))
            alg.setProperty("Dimension1Name", config.get("Dimension1Name"))
            alg.setProperty("Dimension1Binning", config.get("Dimension1Binning", ""))
            alg.setProperty("Dimension2Name", config.get("Dimension2Name"))
            alg.setProperty("Dimension2Binning", config.get("Dimension2Binning", ""))
            alg.setProperty("Dimension3Name", config.get("Dimension3Name"))
            alg.setProperty("Dimension3Binning", config.get("Dimension3Binning", ""))
            alg.setProperty("SymmetryOperations", config.get("SymmetryOperations", ""))
            alg.setProperty("Smoothing", config.get("Smoothing", ""))
            alg.setProperty("OutputWorkspace", config.get("OutputWorkspace"))
            alg.executeAsync()
        except RuntimeError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def finish_make_slice(self, obs, error=False, msg=""):
        """This is the callback from the algorithm observer"""
        if error:
            err_msg = f"Error making slice\n{msg}"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
        else:
            logger.information("Finished making slice")

        self.algorithms_observers.remove(obs)


class MakeSliceObserver(AlgorithmObserver):
    """Object to handle the execution of MakeSlice algorithms"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call parent upon algorithm finishing"""
        self.parent.finish_make_slice(self)

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call parent upon algorithm error"""
        self.parent.finish_make_slice(self, True, msg)


class FileLoadingObserver(AlgorithmObserver):
    """Object to handle the execution events of the loading algorithms"""

    def __init__(self, parent, filename, ws_type, ws_name):
        super().__init__()
        self.parent = parent
        self.filename = filename
        self.ws_type = ws_type
        self.ws_name = ws_name

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call parent upon algorithm finishing"""
        self.parent.finish_loading(self, self.filename, self.ws_type, self.ws_name)

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call parent upon algorithm error"""
        self.parent.finish_loading(self, self.filename, self.ws_type, self.ws_name, True, msg)


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
            self.callback("add", ws, filter_ws(ws), get_frame(ws))

    def deleteHandle(self, ws, _):  # pylint: disable=invalid-name
        """Callback handle for ADS delete"""
        logger.debug(f"deleteHandle: {ws}")
        if self.callback:
            self.callback("del", ws, None)

    def replaceHandle(self, ws, _):  # pylint: disable=invalid-name
        """Callback handle for ADS replace"""
        logger.debug(f"replaceHandle: {ws}")
        self.deleteHandle(ws, None)
        self.addHandle(ws, None)

    def renameHandle(self, old, new):  # pylint: disable=invalid-name
        """Callback handle for ADS rename"""
        logger.debug(f"renameHandle: {old} {new}")
        self.deleteHandle(old, None)
        self.addHandle(new, None)

    def register_call_back(self, callback):
        """Set the callback function for workspace changes"""
        self.callback = callback


def filter_ws(name):
    """Return the type of workspace"""
    ws_id = mtd[name].id()
    ws_type = None

    if ws_id == "MDHistoWorkspace":
        if mtd[name].getSpecialCoordinateSystem().name == "HKL":
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

        # check SpecialCoordinateSystem is either QSample or QLab
        if mde_ws.getSpecialCoordinateSystem().name in ("QSample", "QLab"):
            dim_0 = mde_ws.getDimension(0).getMDFrame().name()
            dim_1 = mde_ws.getDimension(1).getMDFrame().name()
            dim_2 = mde_ws.getDimension(2).getMDFrame().name()
            dim_3 = mde_ws.getDimension(3).name
            # Last dimension must be momentum transfer, DeltaE
            # and the first 3 being either Q_sample or Q_lab
            if (
                dim_3 == "DeltaE"
                and dim_0 in ("QLab", "QSample")
                and dim_1 in ("QLab", "QSample")
                and dim_2 in ("QLab", "QSample")
            ):
                ws_type = "mde"

    if ws_type is None:
        logger.error(f"Unsupported workspace type {ws_id} for {name}")

    return ws_type


def get_frame(name):
    """Returns the MDE frame for the given workspace name"""
    return mtd[name].getSpecialCoordinateSystem().name
