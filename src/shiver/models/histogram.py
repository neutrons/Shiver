"""Model for the Histogram tab"""
import time
import os.path
from typing import Tuple
import numpy as np

# pylint: disable=no-name-in-module
from mantid.api import (
    AlgorithmManager,
    AlgorithmObserver,
    AnalysisDataServiceObserver,
    Progress,
)
from mantid.simpleapi import mtd, DeleteWorkspace, RenameWorkspace, SaveMD
from mantid.kernel import Logger
from mantid.geometry import (
    SymmetryOperationFactory,
    SpaceGroupFactory,
    PointGroupFactory,
)

from shiver.models.generate import GenerateModel
from shiver.models.polarized import PolarizedModel

logger = Logger("SHIVER")


class HistogramModel:  # pylint: disable=too-many-public-methods
    """Histogram model"""

    def __init__(self):
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.ads_observers = ADSObserver()
        self.error_callback = None
        self.warning_callback = None
        self.makeslice_finish_callback = None

    def load(self, filename, ws_type):
        """Method to take filename and workspace type and load with correct algorithm"""
        info_step = ""
        ws_name, _ = os.path.splitext(os.path.basename(filename))
        additional_parameters = {}
        if ws_type == "mde":
            info_step = f"Loading {filename} as MDE"
            logger.information(info_step)
            load = AlgorithmManager.create("LoadMD")
        elif ws_type == "mdh":
            info_step = f"Loading {filename} as MDH"
            logger.information(info_step)
            load = AlgorithmManager.create("LoadMD")
        elif ws_type == "norm":
            info_step = f"Loading {filename} as normalization"
            logger.information(info_step)
            load = AlgorithmManager.create("LoadNexusProcessed")
            additional_parameters = {"LoadHistory": False}
        else:
            logger.error(f"Unsupported workspace type {ws_type} for {filename}")

        endrange = 100
        progress = Progress(load, start=0.0, end=1.0, nreports=endrange)
        progress.report(info_step)
        alg_obs = FileLoadingObserver(self, filename, ws_type, ws_name)
        self.algorithms_observers.add(alg_obs)

        alg_obs.observeFinish(load)
        alg_obs.observeError(load)
        load.initialize()
        load.setLogging(False)
        try:
            load.setProperty("Filename", filename)
            load.setProperty("OutputWorkspace", ws_name)
            for key, value in additional_parameters.items():
                load.setProperty(key, value)
            load.executeAsync()
        except ValueError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def load_dataset(self, dataset: dict) -> Tuple[str, str, str]:  # pylint: disable=too-many-branches
        """Perform dataset loading with given parameters dictionary.

        Parameters
        ----------
        dataset : dict
            Dictionary of parameters for loading the dataset.

        Returns
        -------
        Tuple[str, str, str]
            Tuple of workspace names for data, background and normalization.
        """
        ws_data, ws_background, ws_norm = None, None, None

        # Figure out convention
        if "mde_name" in dataset.keys():
            # new convention
            mde_name_label = "mde_name"
            mde_folder_label = "output_dir"
        else:
            # old convention
            mde_name_label = "MdeName"
            mde_folder_label = "MdeFolder"

        # Data & Background
        mde_name = dataset.get(mde_name_label, None)
        if mde_name is not None:
            if not mtd.doesExist(mde_name):
                mde_folder = dataset.get(mde_folder_label, "")
                mde_file = os.path.join(mde_folder, f"{mde_name}.nxs")
                # check if file exists
                if not os.path.isfile(mde_file):
                    ws_data = self.generate_mde(dataset)
                else:
                    self.load(mde_file, "mde")
                    ws_data = mde_name
            else:
                ws_data = mde_name

        bg_name = dataset.get("BackgroundMdeName", None)
        if bg_name is not None:
            if not mtd.doesExist(bg_name):
                mde_folder = dataset.get(mde_folder_label, "")
                mde_file = os.path.join(mde_folder, f"{bg_name}.nxs")
                # check if file exists
                if not os.path.isfile(mde_file):
                    # self.generate_mde(dataset), not supported at the moment
                    ws_background = None
                else:
                    self.load(mde_file, "mde")
                    ws_background = bg_name
            else:
                ws_background = bg_name

        # Normalization
        norm_data_file = dataset.get("NormalizationDataFile", None)
        if norm_data_file is not None:
            norm_name = os.path.basename(norm_data_file).split(".")[0]
            if not mtd.doesExist(norm_name):
                self.load(norm_data_file, "norm")
            ws_norm = norm_name

        # wait until all the workspaces are loaded
        while not all(mtd.doesExist(ws) for ws in (ws_data, ws_background, ws_norm) if ws is not None):
            time.sleep(0.1)

        return ws_data, ws_background, ws_norm

    def generate_mde(self, config_dict: dict) -> str:
        """Generate MDE workspace from given parameters dictionary."""
        # if old convention, do not proceed
        if "MdeName" in config_dict.keys():
            if self.error_callback:
                self.error_callback("Old convention is not supported.")
            return None

        # make a model of GenerateMDE so that we can use it to call
        # the algorithm directly
        generate_mde_model = GenerateModel()
        # call the algorithm
        # NOTE: this call will
        #       - create the workspace in memory
        #       - save the workspace to file
        generate_mde_model.generate_mde(config_dict)

        return config_dict["mde_name"]

    def delete(self, ws_name):
        """Delete the workspace"""
        DeleteWorkspace(ws_name, EnableLogging=False)

    def rename(self, old_name, new_name):
        """Rename the workspace from old_name to new_name"""
        RenameWorkspace(old_name, new_name)

    def save(self, ws_name, filename):
        """Save the workspace to Nexus file."""
        save_params = {"SaveInstrument": False, "SaveSample": False, "SaveLogs": False}
        SaveMD(ws_name, filename, **save_params)

    def save_to_ascii(
        self,
        ws_name: str,
        filename: str,
        ignore_integrated: bool = False,
        num_ev_norm: bool = False,
        format_str: str = "%.6e",
    ):
        """Save an MDHistoToWorkspace to an ascii file (column format).

        Parameters
        ----------
        ws_name : str
            Name of the workspace to save.
        filename : str
            Name of the file to save to.
        IgnoreIntegrated : bool, optional
            If True, the integrated dimensions are ignored (smaller files), but that information is lost
            (default is False).
        NumEvNorm : bool, optional
            Must be set to true if data was converted to MD from a histogram workspace (like NXSPE)
            and no MDNorm algorithms were used.
        format_str : str, optional
            Format string for the output (default is "%.6e").

        NOTE
        ----
        This function is adapted from DGS_SC_scripts/slice_util.py::SaveMDToAscii.
        """
        # sanity check (workspace must exist)
        if not mtd.doesExist(ws_name):
            if self.error_callback:
                self.error_callback(f"Workspace {ws_name} no longer exist in memory.")
            return

        workspace = mtd[ws_name]

        # sanity check (workspace must be an MDHistoWorkspace)
        if workspace.id() != "MDHistoWorkspace":
            if self.error_callback:
                self.error_callback(f"Workspace {ws_name} is not an MDHistoWorkspace.")
            return

        # get dimensions
        if ignore_integrated:
            dims = workspace.getNonIntegratedDimensions()
        else:
            dims = [workspace.getDimension(i) for i in range(workspace.getNumDims())]
        dimarrays = [dim2array(d) for d in dims]

        if len(dimarrays) > 1:
            newdimarrays = np.meshgrid(*dimarrays, indexing="ij")
        else:
            newdimarrays = dimarrays

        # get data
        data = workspace.getSignalArray() * 1.0
        err2 = workspace.getErrorSquaredArray() * 1.0
        if num_ev_norm:
            nev = workspace.getNumEventsArray()
            data /= nev
            err2 /= nev * nev
        err = np.sqrt(err2)

        # write file
        header = "Intensity Error " + " ".join([d.name for d in dims])
        header += "\n shape: " + "x".join([str(d.getNBins()) for d in dims])
        to_print = np.c_[data.flatten(), err.flatten()]
        for dim in newdimarrays:
            to_print = np.c_[to_print, dim.flatten()]
        np.savetxt(filename, to_print, fmt=format_str, header=header)

    def save_history(self, ws_name, filename):
        """Save the mantid algorithm history"""
        history = mtd[ws_name].getHistory()

        script = [
            "import shiver",
            f"from mantid.simpleapi import {', '.join(set(alg.name() for alg in history.getAlgorithmHistories()))}",
            "",
            "",
        ]

        previous_name = ""
        for alg in history.getAlgorithmHistories():
            alg_name = alg.name()
            if alg_name == "LoadMD" and previous_name == "GenerateDGSMDE":
                comment = "# "
            else:
                comment = ""
            previous_name = alg_name
            separator = ",\n" + comment + "\t"
            alg_props = []
            for prop in alg.getProperties():
                default = prop.isDefault()
                value = prop.value()
                if value and not default:
                    value = value.replace('"', "'")
                    alg_props.append(f'{prop.name()}="{value}"')
            alg_props = separator.join(alg_props)
            script.append(f"{comment}{alg_name}({alg_props})")

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

    def connect_warning_message(self, callback):
        """Set the callback function for error messages"""
        self.warning_callback = callback

    def connect_makeslice_finish(self, callback):
        """Set the callback function for makeslice finish"""
        self.makeslice_finish_callback = callback

    def symmetry_operations(self, symmetry):
        """Validate the symmetry value with mantid"""
        if len(symmetry) != 0:
            try:
                if SpaceGroupFactory.isSubscribedSymbol(symmetry) or PointGroupFactory.isSubscribed(symmetry):
                    # then it's valid
                    logger.information(f"Symmetry {symmetry} is valid!")
                else:
                    # check with SymmetryOperationFactory.createSymOps
                    try:
                        SymmetryOperationFactory.createSymOps(symmetry)
                        logger.information(f"Symmetry {symmetry} is valid!")
                    except RuntimeError as err:
                        err_msg = f"Invalid Symmetry Operations value. {err} \n"
                        logger.error(err_msg)
                        if self.error_callback:
                            self.error_callback(err_msg, accumulate=True)
                        return False
            except RuntimeError as err:
                err_msg = f"Invalid Symmetry Operations value. {err} \n"
                logger.error(err_msg)
                if self.error_callback:
                    self.error_callback(err_msg, accumulate=True)
                return False
        return True

    def ws_change_call_back(self, callback):
        """Set the callback function for workspace changes"""
        self.ads_observers.register_call_back(callback)

    def get_all_valid_workspaces(self):
        """Get all existing workspaces"""
        return (
            (name, filter_ws(name), get_frame(name), get_num_non_integrated_dims(name))
            for name in mtd.getObjectNames()
            if filter_ws(name)
        )

    def get_plot_display_name(self, ws_name, ndims):
        """Method retrieve all dimension names, minimum and maximum for displaying in the plot"""
        workspace = mtd[ws_name]
        display_name = f"{ws_name}"
        if ndims <= 2:
            # collect dimensions min and max for 1D and 2D plots
            display_name += ":"
            for dim in range(ndims, workspace.getNumDims()):
                dimension = workspace.getDimension(dim)
                dim_min = round(dimension.getMinimum(), 2)
                dim_max = round(dimension.getMaximum(), 2)
                dim_name = dimension.name
                display_name += f" {dim_min}<{dim_name}<{dim_max}"
                display_name += "," if dim < (workspace.getNumDims() - 1) else ""
        return display_name

    def validate_workspace_logs(self, config: dict):
        """Method to validate sample logs and flipping ratios of SF and NSF workspaces"""
        # find the flipping ratio
        # SpinFlip workspace
        # init PolarizedModel
        polarized_model = PolarizedModel(config.get("SFInputWorkspace"))
        sf_flipping_ratio = polarized_model.get_flipping_ratio()

        # NonSpinflip workspace
        # init PolarizedModel
        polarized_model = PolarizedModel(config.get("NSFInputWorkspace"))
        nsf_flipping_ratio = polarized_model.get_flipping_ratio()

        # compare the flipping ratios of the two workspaces gathered from sample logs
        # depending on the error status and user input
        # the flag indicates whether flipping ratios are valid and we can continue with execution
        continue_with_algorithm = False

        if sf_flipping_ratio is not None and nsf_flipping_ratio is None:
            # case 1 only SF is there
            # return warning
            err = f"""FlippingRatio Sample Log value is defined only in SF.
                {sf_flipping_ratio} will be used. Would you like to continue?"""
            if self.warning_callback:
                continue_with_algorithm = self.warning_callback(str(err))
        elif sf_flipping_ratio is not None and nsf_flipping_ratio is not None:
            # case 2 both are there
            if sf_flipping_ratio != nsf_flipping_ratio:
                # case 2.1 ratios do not much
                # return warning
                # at least one should be there
                err = f"""FlippingRatio Sample Log value is different between workspaces.
                    SF :{sf_flipping_ratio} and NSF: {nsf_flipping_ratio}.
                    SF will be used. Would you like to continue?"""
                if self.warning_callback:
                    continue_with_algorithm = self.warning_callback(str(err))
            else:
                continue_with_algorithm = True
        else:
            # case 3 neither are there
            # return error
            # they should be there
            err = "FlippingRatio Sample Log value is missing/invalid from both workspaces."
            logger.error(err)
            if self.error_callback:
                self.error_callback(err)
        return continue_with_algorithm

    def do_make_slice(self, config: dict):
        """Method to take filename and workspace type and load with correct algorithm"""
        # remove the OutputWorkspaces first if they exist
        if config.get("OutputWorkspace") and mtd.doesExist(config["OutputWorkspace"]):
            self.delete(config["OutputWorkspace"])

        if config.get("SFOutputWorkspace") and mtd.doesExist(config["SFOutputWorkspace"]):
            self.delete(config["SFOutputWorkspace"])

        if config.get("NSFOutputWorkspace") and mtd.doesExist(config["NSFOutputWorkspace"]):
            self.delete(config["NSFOutputWorkspace"])

        alg = AlgorithmManager.create(config["Algorithm"])
        if config["Algorithm"] == "MakeSlice":
            alg_obs = MakeSliceObserver(parent=self, ws_names=[config.get("OutputWorkspace")])
        else:
            # primary/default workspace is SFOutputWorkspace
            # secondary workspace is NSFOutputWorkspace
            alg_obs = MakeSliceObserver(
                parent=self, ws_names=[config.get("SFOutputWorkspace"), config.get("NSFOutputWorkspace")]
            )

            # get the flipping ratio of sf
            # init PolarizedModel
            polarized_model = PolarizedModel(config.get("SFInputWorkspace"))
            flipping_ratio = polarized_model.get_experiment_sample_log("FlippingRatio")
            sample_log = polarized_model.get_experiment_sample_log("FlippingRatioSampleLog")

            config["FlippingRatio"] = flipping_ratio
            config["FlippingRatioSampleLog"] = ""
            if sample_log is not None:
                config["FlippingRatioSampleLog"] = sample_log

        # add to observers
        self.algorithms_observers.add(alg_obs)
        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)
        alg.initialize()
        alg.setLogging(False)
        try:
            if config["Algorithm"] == "MakeSlice":
                alg.setProperty("InputWorkspace", config.get("InputWorkspace"))
                alg.setProperty("OutputWorkspace", config.get("OutputWorkspace"))

            else:
                alg.setProperty("SFInputWorkspace", config.get("SFInputWorkspace"))
                alg.setProperty("NSFInputWorkspace", config.get("NSFInputWorkspace"))
                alg.setProperty("SFOutputWorkspace", config.get("SFOutputWorkspace"))
                alg.setProperty("NSFOutputWorkspace", config.get("NSFOutputWorkspace"))
                alg.setProperty("FlippingRatio", config.get("FlippingRatio"))
                alg.setProperty("FlippingRatioSampleLog", config.get("FlippingRatioSampleLog", ""))

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
            alg.executeAsync()
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def finish_make_slice(self, obs, ws_names, error=False, msg=""):
        """This is the callback from the algorithm observer"""

        workspaces = ",".join(ws_names)
        dimensions = {}
        for workspace in ws_names:
            dimensions[workspace] = -1
        if error:
            err_msg = f"Error making slice for {workspaces}\n{msg}"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            if self.makeslice_finish_callback:
                self.makeslice_finish_callback(dimensions, error)
        else:
            for workspace in ws_names:
                dimensions[workspace] = get_num_non_integrated_dims(workspace)
            logger.information(f"Finished making slice(s) {workspaces}")
            if self.makeslice_finish_callback:
                self.makeslice_finish_callback(dimensions, error)
        self.algorithms_observers.remove(obs)

    def get_make_slice_history(self, name) -> dict:
        """Get the history of the last applied MakeSlice/s algorithm.

        Parameters
        ----------
        name : str
            The name of the histogram workspace for history retrieval

        Returns
        -------
        dict
            A dictionary of the history of the make slice algorithm
        """
        history_dict = {}
        if mtd.doesExist(name):
            histogram_ws = mtd[name]
            alg_history = histogram_ws.getHistory().getAlgorithmHistories()
            # look for the last make slice algorithm used
            for alg in reversed(alg_history):
                if alg.name() == "MakeSlice" or alg.name() == "MakeSFCorrectedSlices":
                    history_dict["Algorithm"] = alg.name()
                    for prop in alg.getProperties():
                        history_dict[prop.name()] = prop.value()
                    break
            # Quick sanity check to make sure the workspaces are still in memory
            # If output workspace no longer in memory, replace with ""
            if history_dict["Algorithm"] == "MakeSlice":
                # for make slice
                # - input workspace
                if not mtd.doesExist(history_dict.get("InputWorkspace", "")):
                    history_dict["InputWorkspace"] = ""
            else:
                # for makemultiple slices
                # - spin flip workspace
                if not mtd.doesExist(history_dict.get("SFInputWorkspace", "")):
                    history_dict["SFInputWorkspace"] = ""
                # - non-spin flip workspace
                if not mtd.doesExist(history_dict.get("NSFInputWorkspace", "")):
                    history_dict["NSFInputWorkspace"] = ""

            # - background workspace
            if not mtd.doesExist(history_dict.get("BackgroundWorkspace", "")):
                history_dict["BackgroundWorkspace"] = ""
            # - normalization workspace
            if not mtd.doesExist(history_dict.get("NormalizationWorkspace", "")):
                history_dict["NormalizationWorkspace"] = ""

        return history_dict


class MakeSliceObserver(AlgorithmObserver):
    """Object to handle the execution of MakeSlice algorithms"""

    def __init__(self, parent, ws_names):
        super().__init__()
        self.parent = parent
        # array of workspace names
        self.ws_names = ws_names

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call parent upon algorithm finishing"""
        self.parent.finish_make_slice(self, self.ws_names)

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call parent upon algorithm error"""
        self.parent.finish_make_slice(self, self.ws_names, True, msg)


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
            self.callback("add", ws, filter_ws(ws), get_frame(ws), get_num_non_integrated_dims(ws))

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
        logger.notice(f"Unsupported workspace type {ws_id} for {name}")

    return ws_type


def get_frame(name):
    """Returns the MDE frame for the given workspace name"""
    if hasattr(mtd[name], "getSpecialCoordinateSystem"):
        return mtd[name].getSpecialCoordinateSystem().name
    return None


def get_num_non_integrated_dims(name):
    """Returns the number of non-integrated dimensions"""
    if hasattr(mtd[name], "getNonIntegratedDimensions"):
        return len(mtd[name].getNonIntegratedDimensions())
    return -1


def dim2array(dim, center=True) -> np.ndarray:
    """
    Create a numpy array containing bin centers along the dimension d.

    Parameters
    ----------
    dim: IMDDimension
    center: bool, optional

    Returns
    -------
        from min+st/2 to max-st/2 with step st
    """
    dmin = dim.getMinimum()
    dmax = dim.getMaximum()
    dstep = dim.getX(1) - dim.getX(0)
    if center:
        return np.arange(dmin + dstep / 2, dmax, dstep)

    return np.linspace(dmin, dmax, dim.getNBins() + 1)
