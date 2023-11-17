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
        return get_polarization_logs_for_workspace(self.workspace_name)


def get_polarization_logs_for_workspace(workspace):
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
        sample_log_data[sample_log] = get_experiment_sample_log(workspace, sample_log)
    return sample_log_data


def get_flipping_ratio(workspace):
    """Method to return the flipping ratio for a workspace"""

    # get flipping ratio and flippingsamplelog values
    flipping_formula = get_experiment_sample_log(workspace, "FlippingRatio")
    sample_log = get_experiment_sample_log(workspace, "FlippingRatioSampleLog")

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


def get_experiment_sample_log(name, log_name):
    """Get the sample log with name"""
    log_value = None
    if name and mtd.doesExist(name):
        workspace = mtd[name]
        if hasattr(workspace, "getExperimentInfo"):
            try:
                run = workspace.getExperimentInfo(0).run()
                if log_name in run.keys():
                    if run.getLogData(log_name).type == "string":
                        log_value = run.getLogData(log_name).value
                    else:
                        log_value = run.getPropertyAsSingleValueWithTimeAveragedMean(log_name)
            except ValueError as err:
                logger.error(f"Experiment info error {err}.")
    return log_value
