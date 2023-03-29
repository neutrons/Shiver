"""Model for Corrections tab"""
# pylint: disable=no-name-in-module
from mantid.api import AlgorithmManager, AlgorithmObserver
from mantid.kernel import Logger

logger = Logger("SHIVER")

class CorrectionsModel:
    """Corrections table model"""

    def __init__(self) -> None:
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.error_callback = None

    def apply_detailed_balance(
            self,
            ws_name: str,
            temperature: str,
            output_ws_name:str,
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

    def apply_detailed_balance_finished(
            self,
            ws_name: str,
            alg: "ApplyDetailedBalanceMDObserver",
            error: bool=False,
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
            error: bool=False,
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
        self.parent.apply_scattered_transmission_correction_finished(ws_name=self.ws_name, alg=self, error=False, msg="")

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call upon algorithm error"""
        self.parent.apply_scattered_transmission_correction_finished(ws_name=self.ws_name, alg=self, error=True, msg=msg)
