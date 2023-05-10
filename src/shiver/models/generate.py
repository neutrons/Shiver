"""Model for the Generate tab"""
from mantid.api import (  # pylint: disable=no-name-in-module
    AlgorithmManager,
    AlgorithmObserver,
)
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    mtd,
)
from mantid.kernel import (  # pylint: disable=no-name-in-module
    Logger,
    Property,
)

logger = Logger("SHIVER")


# pylint: disable=too-few-public-methods
class GenerateModel:
    """Generate model"""

    workspace_name = None
    output_dir = None

    def __init__(self):
        self.algorithm_observer = set()  # keep running in scope
        self.error_callback = None

    def connect_error_message(self, callback):
        """Connect error message"""
        self.error_callback = callback

    def generate_mde(self, config_dict: dict):
        """Call GenerateDGSMDE algorithm

        Parameters
        ----------
        config_dict : dict
            Configuration dictionary
        """
        # remove output workspace if it exists in memory
        output_workspace = config_dict.get("mde_name", "")
        if output_workspace and mtd.doesExist(output_workspace):
            mtd.remove(output_workspace)

        # create algorithm via AlgorithmManager (for async execution)
        alg = AlgorithmManager.create("GenerateDGSMDE")
        alg_obs = GenerateMDEObserver(parent=self)
        self.algorithm_observer.add(alg_obs)

        # add alg to observer
        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)

        # prep
        alg.initialize()
        alg.setLogging(False)  # avoid noisy output

        # Demo config_dict from view
        # {
        #     'mde_name': 'test',
        #     'output_dir': '/tmp',
        #     'mde_type': 'Data',
        #     'filename': "file1.nxs+file2.nxs, file3.nxs",
        #     'MaskingDataFile': '/home/8cz/Github/Shiver/tests/data/raw/ub_process_nexus.nxs',
        #     'NormalizationDataFile': '/home/8cz/Github/Shiver/tests/data/raw/ub_process_nexus.nxs',
        #     'Ei': '5',
        #     'T0': '0',
        #     'AdvancedOptions': {
        #         'MaskInputs': [{'Bank': '1', 'Tube': '2', 'Pixel': '3'}],
        #         'E_min': '1',
        #         'E_max': '2',
        #         'ApplyFilterBadPulses': True,
        #         'BadPulsesThreshold': '95',
        #         'TimeIndepBackgroundWindow': 'Default',
        #         'Goniometer': 'x',
        #         'AdditionalDimensions': 'x,1,2'
        #         },
        #     'SampleParameters': {
        #         'a': '1.00000',
        #         'b': '1.00000',
        #         'c': '1.00000',
        #         'alpha': '90.00000',
        #         'beta': '90.00000',
        #         'gamma': '90.00000',
        #         'u': '0.00000,0.00000,1.00000',
        #         'v': '1.00000,0.00000,-0.00000',
        #         'matrix_ub': '1.00000,0.00000,0.00000,0.00000,1.00000,0.00000,0.00000,-0.00000,1.00000',
        #         },
        #     'PolarizedOptions': {
        #         'PolarizationState': 'SF_Pz',
        #         'FlippingRatio': '1+x',
        #         'PSDA': '1',
        #         'SampleLog': 'x',
        #         }
        # }

        # extract parameters from config_dict
        # Mandatory
        filenames = config_dict.get("filename", "")
        type_input = config_dict.get("mde_type", "Data")
        output_workspace = config_dict.get("mde_name", "outws")

        self.workspace_name = output_workspace
        self.output_dir = config_dict.get("output_dir", "")

        # Optional
        mask_file = config_dict.get("MaskingDataFile", "")
        incident_energy = config_dict.get("Ei", Property.EMPTY_DBL)
        incident_t0 = config_dict.get("T0", Property.EMPTY_DBL)
        #
        advanced_options = config_dict.get("AdvancedOptions", {})
        mask_inputs = str(advanced_options.get("MaskInputs", ""))
        apply_filter_bad_pulses = advanced_options.get("ApplyFilterBadPulses", False)
        bad_pulse_threshold = advanced_options.get("BadPulsesThreshold", Property.EMPTY_DBL)
        omega_motor_name = advanced_options.get("Goniometer", "")
        additional_dimensions = advanced_options.get("AdditionalDimensions", "")
        minimum_energy_transfer = advanced_options.get("EMin", Property.EMPTY_DBL)
        maximum_energy_transfer = advanced_options.get("EMax", Property.EMPTY_DBL)
        time_indepedent_background = advanced_options.get("TimeIndepBackgroundWindow", "")
        #
        sample_parameters = config_dict.get("SampleParameters", {})
        # remove matrix_ub from sample_parameters
        sample_parameters.pop("matrix_ub", "")
        ub_parameters = str(sample_parameters)
        #
        polarized_options = config_dict.get("PolarizedOptions", {})
        polarizing_supermirror_defection_angle = polarized_options.get("PSDA", Property.EMPTY_DBL)

        # execute
        try:
            alg.setProperty("Filenames", filenames)
            alg.setProperty("MaskFile", mask_file)
            alg.setProperty("MaskInputs", mask_inputs)
            alg.setProperty("ApplyFilterBadPulses", apply_filter_bad_pulses)
            alg.setProperty("BadPulsesThreshold", bad_pulse_threshold)
            alg.setProperty("OmegaMotorName", omega_motor_name)
            alg.setProperty("Ei", incident_energy)
            alg.setProperty("T0", incident_t0)
            alg.setProperty("EMin", minimum_energy_transfer)
            alg.setProperty("EMax", maximum_energy_transfer)
            alg.setProperty("TimeIndependentBackground", time_indepedent_background)
            alg.setProperty("PolarizingSupermirrorDeflectionAdjustment", polarizing_supermirror_defection_angle)
            if additional_dimensions:
                # NOTE: AdditionalDimensions does not have a default value, and
                #       mantid does not know how to handle empty string, so
                #       we need to check if it is empty before setting it.
                alg.setProperty("AdditionalDimensions", additional_dimensions)
            alg.setProperty("Type", type_input)
            alg.setProperty("UBParameters", ub_parameters)
            alg.setProperty("OutputWorkspace", output_workspace)
            alg.execute()
        except RuntimeError as err:
            # NOTE: this error is usually related to incorrect input that triggers
            #       error during alg start-up, execution error will be captured
            #       by the obs handlers.
            logger.error(f"Error in GenerateDGSMDE:\n{err}")
            if self.error_callback:
                self.error_callback(
                    msg=f"Error in GenerateDGSMDE:\n{err}",
                    accumulate=True,
                )

    def finish_generate_mde(self, obs, error=False, msg=""):
        """Callback from algorithm observer for GenerateDGSMDE

        Parameters
        ----------
        obs : AlgorithmObserver
            Observer of the algorithm
        error : bool, optional
            Error flag, by default False
        msg : str, optional
            Error message, by default ""
        """
        if error:
            err_msg = f"Error in GenerateDGSMDE:\n{msg}"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            #
            self.workspace_name = None
            self.output_dir = None
        else:
            logger.information("GenerateDGSMDE finished")

        self.algorithm_observer.remove(obs)

        # kick off the saving


class GenerateMDEObserver(AlgorithmObserver):
    """Observer to handle the execution of GenerateDGSMDE"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call parent upon completion of algorithm"""
        self.parent.finish_generate_mde(obs=self, error=False, msg="")

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call parent upon error of algorithm"""
        self.parent.finish_generate_mde(obs=self, error=True, msg=msg)
