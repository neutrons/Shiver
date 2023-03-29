"""Model for Corrections tab"""
# pylint: disable=no-name-in-module
import time
from typing import Tuple
from mantid.api import mtd, AlgorithmManager, AlgorithmObserver
from mantid.kernel import Logger

logger = Logger("SHIVER")


class CorrectionsModel:
    """Corrections table model"""

    def __init__(self) -> None:
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.error_callback = None

    def apply(
        self,
        ws_name: str,
        detailed_balance: bool,
        hyspec_polarizer_transmission: bool,
        temperature: str = "",
    ) -> None:
        """Apply corrections"""
        output_ws_name = f"{ws_name}_correction"
        if detailed_balance:
            self.apply_detailed_balance(
                ws_name,
                temperature,
                output_ws_name,
            )
        #
        if hyspec_polarizer_transmission:
            input_ws_name = ws_name
            if detailed_balance:
                # wait for detailed balance to finish
                while not mtd.doesExist(output_ws_name):
                    time.sleep(0.1)
                input_ws_name = output_ws_name
            self.apply_scattered_transmission_correction(
                input_ws_name,
                output_ws_name,
            )

    def apply_detailed_balance(
        self,
        ws_name: str,
        temperature: str,
        output_ws_name: str,
    ) -> None:
        """Apply detailed balance to the workspace"""
        alg_obs = ApplyDetailedBalanceMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        alg = AlgorithmManager.create("ApplyDetailedBalanceMD")

        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)

        alg.initialize()
        alg.setLogging(False)
        try:
            alg.setProperty("InputWorkspace", ws_name)
            alg.setProperty("Temperature", temperature)
            alg.setProperty("OutputWorkspace", output_ws_name)
            alg.executeAsync()
        except ValueError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def apply_scattered_transmission_correction(
        self,
        ws_name: str,
        output_ws_name: str,
    ) -> None:
        """Apply DGSScatterTransmissionCorrection to the workspace"""
        alg_obs = DgsScatteredTransmissionCorrectionMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        exponent_factor = 1.0 / 11.0  # fixed value

        logger.information(f"Applying DGS Scattered Transmission Correction with exponent factor {exponent_factor}")
        alg = AlgorithmManager.create("DgsScatteredTransmissionCorrectionMD")

        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)

        alg.initialize()
        alg.setLogging(False)
        try:
            alg.setProperty("InputWorkspace", ws_name)
            alg.setProperty("ExponentFactor", exponent_factor)
            alg.setProperty("OutputWorkspace", output_ws_name)
            alg.executeAsync()
        except ValueError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def apply_detailed_balance_finished(
        self,
        ws_name: str,
        alg: "ApplyDetailedBalanceMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when ApplyDetailedBalanceMD finishes"""
        if error:
            logger.error(f"Error in ApplyDetailedBalanceMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished ApplyDetailedBalanceMD for {ws_name}")
        self.algorithms_observers.remove(alg)

    def apply_scattered_transmission_correction_finished(
        self,
        ws_name: str,
        alg: "DgsScatteredTransmissionCorrectionMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when DgsScatteredTransmissionCorrectionMD finishes"""
        if error:
            logger.error(f"Error in DgsScatteredTransmissionCorrectionMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished DgsScatteredTransmissionCorrectionMD for {ws_name}")
        self.algorithms_observers.remove(alg)

    def get_ws_alg_histories(self, ws_name: str) -> list:
        """Get algorithm histories of the workspace"""
        if mtd.doesExist(ws_name):
            return mtd[ws_name].getHistory().getAlgorithmHistories()
        return []

    def has_apply_detailed_balance(self, ws_name: str) -> Tuple[bool, str]:
        """Check if the workspace has ApplyDetailedBalanceMD applied"""
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "ApplyDetailedBalanceMD":
                return True, alg_history.getPropertyValue("Temperature")
        return False, ""

    def has_scattered_transmission_correction(self, ws_name: str) -> bool:
        """Check if the workspace has DgsScatteredTransmissionCorrectionMD applied"""
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "DgsScatteredTransmissionCorrectionMD":
                return True
        return False


class ApplyDetailedBalanceMDObserver(AlgorithmObserver):
    """Observer for ApplyDetailedBalanceMD algorithm"""

    def __init__(self, parent, ws_name: str) -> None:
        super().__init__()
        self.parent = parent
        self.ws_name = ws_name

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call upon algorithm finishing"""
        self.parent.apply_detailed_balance_finished(ws_name=self.ws_name, alg=self, error=False, msg="")

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call upon algorithm error"""
        self.parent.apply_detailed_balance_finished(ws_name=self.ws_name, alg=self, error=True, msg=msg)


class DgsScatteredTransmissionCorrectionMDObserver(AlgorithmObserver):
    """Observer for DgsScatteredTransmissionCorrectionMD algorithm"""

    def __init__(self, parent, ws_name: str) -> None:
        super().__init__()
        self.parent = parent
        self.ws_name = ws_name

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call upon algorithm finishing"""
        self.parent.apply_scattered_transmission_correction_finished(
            ws_name=self.ws_name, alg=self, error=False, msg=""
        )

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call upon algorithm error"""
        self.parent.apply_scattered_transmission_correction_finished(
            ws_name=self.ws_name, alg=self, error=True, msg=msg
        )
