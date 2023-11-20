"""Model for the Sample Parameters dialog"""
# pylint: disable=no-name-in-module
from mantid.simpleapi import mtd, AddSampleLog
from mantid.kernel import Logger


logger = Logger("SHIVER")


class PolarizedModel:
    """Polarized model"""

    def __init__(self, workspace_name=None):
        self.error_callback = None
        self.workspace_name = workspace_name

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def save_experiment_sample_log(self, log_name, log_value):
        """Add the sample log with log_name and log_value in the workspace with name"""
        if self.workspace_name and mtd.doesExist(self.workspace_name):
            workspace = mtd[self.workspace_name]
            AddSampleLog(workspace, LogName=log_name, LogText=log_value, LogType="String")

    def save_polarization_logs(self, polarization_logs):
        """Save polarization logs in workspace"""
        if self.workspace_name and mtd.doesExist(self.workspace_name):
            for pol_log, value in polarization_logs.items():
                self.save_experiment_sample_log(pol_log, value)

    def get_polarization_logs(self):
        """Get polarization logs from workspace"""
        return self.get_polarization_logs_for_workspace()

    def get_experiment_sample_log(self, log_name):
        """Get the sample log with name"""
        log_value = None
        if self.workspace_name and mtd.doesExist(self.workspace_name):
            workspace = mtd[self.workspace_name]
            if hasattr(workspace, "getExperimentInfo"):
                try:
                    run = workspace.getExperimentInfo(0).run()
                    if log_name in run.keys():
                        if run.getLogData(log_name).type == "string":
                            log_value = run.getLogData(log_name).value
                        else:
                            log_value = run.getPropertyAsSingleValueWithTimeAveragedMean(log_name)
                except ValueError as err:
                    err_msg = f"Experiment info error {err}."
                    logger.error(err_msg)
        return log_value

    def save_polarization_state(self, pol_state):
        """Save the polarization state as Sample Log in workspace"""
        # valid pol_states should be: UNP, SF or NSF
        if pol_state in ["UNP", "SF", "NSF"]:
            self.save_experiment_sample_log("PolarizationState", pol_state)
            if pol_state in ["SF", "NSF"]:
                polarization_direction_log = self.get_experiment_sample_log("PolarizationDirection")
                if polarization_direction_log is None:
                    # add default polarization direction if it does not exist
                    self.save_experiment_sample_log("PolarizationDirection", "Pz")
        else:
            err_msg = "Invalid polarization state"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)

    def get_polarization_state(self):
        """Get the polarization state from Sample Log in workspace"""
        pol_state = self.get_experiment_sample_log("PolarizationState")
        if pol_state is None:
            # revert to default unpolarized state
            pol_state = "UNP"
        return pol_state

    def get_polarization_logs_for_workspace(self):
        """Get polarization logs from workspace"""
        pol_sample_logs = [
            "PolarizationState",
            "PolarizationDirection",
            "FlippingRatio",
            "FlippingRatioSampleLog",
            "psda",
        ]
        sample_log_data = {}
        for sample_log in pol_sample_logs:
            sample_log_data[sample_log] = self.get_experiment_sample_log(sample_log)
        return sample_log_data

    def get_flipping_ratio(self):
        """Method to return the flipping ratio for a workspace"""

        # get flipping ratio and flippingsamplelog values
        flipping_formula = self.get_experiment_sample_log("FlippingRatio")
        sample_log = self.get_experiment_sample_log("FlippingRatioSampleLog")

        # calculate the flipping ratio
        flipping_ratio = None
        if flipping_formula is not None:
            try:
                # case 1 flipping formula is a number
                flipping_ratio = float(flipping_formula)
            except ValueError:
                # case 2 flipping formula is an expression
                if sample_log is not None:
                    flipping_ratio = f"{flipping_formula},{sample_log}"
                else:
                    err = f"{flipping_formula} is invalid!"
                    logger.error(err)
        return flipping_ratio
