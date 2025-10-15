"""Model for Corrections tab"""

# pylint: disable=no-name-in-module
# pylint: disable=too-many-branches
# pylint: disable=invalid-name
import time
from typing import Tuple

from mantid.api import AlgorithmManager, AlgorithmObserver, mtd
from mantid.kernel import Logger

logger = Logger("SHIVER")


class CorrectionsModel:
    """Corrections table model"""

    def __init__(self) -> None:
        self.algorithms_observers = set()  # need to add them here so they stay in scope
        self.error_callback = None
        self.algorithm_running = False

    def apply(
        self,
        ws_name: str,
        detailed_balance: bool,
        hyspec_polarizer_transmission: bool,
        temperature: str = "",
        debye_waller_factor: bool = False,
        u2: str = "",
        magentic_structure_factor: bool = False,
        ion_name: str = "",
    ) -> None:
        """Apply corrections.

        Parameters
        ----------
        ws_name : str
            Workspace name
        detailed_balance : bool
            Apply detailed balance
        hyspec_polarizer_transmission : bool
            Apply HYSPEC polarizer transmission correction
        temperature : str, optional
            Temperature value as string or log entry contains temperature, by default ""

        Return
        ------
        None

        Note
        ----
        The applied correction is noted as the suffix of the workspace name
          - detailed balance: "_DB"
          - HYSPEC polarizer transmission: "_PT"
        """
        # decide the final output workspace name
        output_ws_name = ws_name
        if detailed_balance:
            output_ws_name = f"{ws_name}_DB"
        if hyspec_polarizer_transmission:
            output_ws_name = f"{output_ws_name}_PT"
        if debye_waller_factor:
            output_ws_name = f"{output_ws_name}_DWF"
        if magentic_structure_factor:
            output_ws_name = f"{output_ws_name}_MSF"

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
                while self.algorithm_running:
                    time.sleep(0.1)
                input_ws_name = output_ws_name
            self.apply_scattered_transmission_correction(
                input_ws_name,
                output_ws_name,
            )

        if magentic_structure_factor:
            input_ws_name = ws_name
            if hyspec_polarizer_transmission or detailed_balance:
                # wait for others to finish
                while self.algorithm_running:
                    time.sleep(0.1)
                input_ws_name = output_ws_name
            self.apply_magnetic_form_factor_correction(
                input_ws_name,
                ion_name,
                output_ws_name,
            )
        if debye_waller_factor:
            input_ws_name = ws_name
            if hyspec_polarizer_transmission or detailed_balance or magentic_structure_factor:
                # wait for others to finish
                while self.algorithm_running:
                    time.sleep(0.1)
                input_ws_name = output_ws_name
            self.apply_debye_waller_factor_correction(
                input_ws_name,
                u2,
                output_ws_name,
            )

    def apply_detailed_balance(
        self,
        ws_name: str,
        temperature: str,
        output_ws_name: str,
    ) -> None:
        """Apply detailed balance to the workspace.

        Parameters
        ----------
        ws_name : str
            Workspace name
        temperature : str
            Temperature value as string or log entry contains temperature
        output_ws_name : str
            Output workspace name

        Returns
        -------
        None
        """
        alg_obs = ApplyDetailedBalanceMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        self.algorithm_running = True

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
        except RuntimeError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            self.algorithm_running = False

    def apply_scattered_transmission_correction(
        self,
        ws_name: str,
        output_ws_name: str,
    ) -> None:
        """Apply DGSScatterTransmissionCorrection to the workspace.

        ref: IOP Conf. Series: Journal of Physics: Conf. Series 862 (2017) 012023
             `Figure 3 Right <https://doi:10.1088/1742-6596/862/1/012023>`_

        Parameters
        ----------
        ws_name : str
            Workspace name
        output_ws_name : str
            Output workspace name

        Returns
        -------
        None
        """
        alg_obs = DgsScatteredTransmissionCorrectionMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        self.algorithm_running = True

        exponent_factor = 1.0 / 11.0  # see ref above

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
        except RuntimeError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            self.algorithm_running = False

    def apply_magnetic_form_factor_correction(
        self,
        ws_name: str,
        ion_name: str,
        output_ws_name: str,
    ) -> None:
        """Apply MagneticFormFactorCorrection to the workspace.

        Parameters
        ----------
        ws_name : str
            Workspace name
        ion_name : str
            Ion name
        output_ws_name : str
            Output workspace name

        Returns
        -------
        None
        """

        alg_obs = MagneticFormFactorCorrectionMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        self.algorithm_running = True

        logger.information(f"Applying Magnetic Form Factor Correction with ion name {ion_name}")

        alg = AlgorithmManager.create("MagneticFormFactorCorrectionMD")
        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)

        alg.initialize()
        alg.setLogging(False)
        try:
            alg.setProperty("InputWorkspace", ws_name)
            alg.setProperty("IonName", ion_name)
            alg.setProperty("OutputWorkspace", output_ws_name)
            alg.execute()
        except RuntimeError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            self.algorithm_running = False

    def apply_debye_waller_factor_correction(
        self,
        ws_name: str,
        u2: str,
        output_ws_name: str,
    ) -> None:
        """Apply DebyeWallerFactorCorrection to the workspace.

        Parameters
        ----------
        ws_name : str
            Workspace name
        u2 : str
            Mean squared displacement
        output_ws_name : str
            Output workspace name

        Returns
        -------
        None
        """

        alg_obs = DebyeWallerFactorCorrectionMDObserver(
            parent=self,
            ws_name=ws_name,
        )
        self.algorithms_observers.add(alg_obs)

        self.algorithm_running = True

        logger.information(f"Applying Debye-Waller Factor Correction with mean squared displacement value {u2}")

        alg = AlgorithmManager.create("DebyeWallerFactorCorrectionMD")
        alg_obs.observeFinish(alg)
        alg_obs.observeError(alg)

        alg.initialize()
        alg.setLogging(False)
        try:
            alg.setProperty("InputWorkspace", ws_name)
            alg.setProperty("MeanSquaredDisplacement", u2)
            alg.setProperty("OutputWorkspace", output_ws_name)
            alg.execute()
        except RuntimeError as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            self.algorithm_running = False

    def connect_error_message(self, callback):
        """Set the callback function for error messages.

        Parameters
        ----------
        callback : function
            Callback function

        Returns
        -------
        None
        """
        self.error_callback = callback

    def apply_detailed_balance_finished(
        self,
        ws_name: str,
        alg: "ApplyDetailedBalanceMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when ApplyDetailedBalanceMD finishes.

        Parameters
        ----------
        ws_name : str
            Workspace name
        alg : ApplyDetailedBalanceMDObserver
            Observer
        error : bool, optional
            Error flag, by default False
        msg : str, optional
            Error message, by default ""

        Returns
        -------
        None
        """
        if error:
            logger.error(f"Error in ApplyDetailedBalanceMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished ApplyDetailedBalanceMD for {ws_name}")
        self.algorithms_observers.remove(alg)
        self.algorithm_running = False

    def apply_scattered_transmission_correction_finished(
        self,
        ws_name: str,
        alg: "DgsScatteredTransmissionCorrectionMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when DgsScatteredTransmissionCorrectionMD finishes.

        Parameters
        ----------
        ws_name : str
            Workspace name
        alg : DgsScatteredTransmissionCorrectionMDObserver
            Observer
        error : bool, optional
            Error flag, by default False
        msg : str, optional
            Error message, by default ""

        Returns
        -------
        None
        """
        if error:
            logger.error(f"Error in DgsScatteredTransmissionCorrectionMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished DgsScatteredTransmissionCorrectionMD for {ws_name}")
        self.algorithms_observers.remove(alg)
        self.algorithm_running = False

    def apply_magnetic_form_factor_correction_finished(
        self,
        ws_name: str,
        alg: "MagneticFormFactorCorrectionMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when MagneticFormFactorCorrectionMD finishes.

        Parameters
        ----------
        ws_name : str
            Workspace name
        alg : MagneticFormFactorCorrectionMDObserver
            Observer
        error : bool, optional
            Error flag, by default False
        msg : str, optional
            Error message, by default ""

        Returns
        -------
        None
        """
        if error:
            logger.error(f"Error in MagneticFormFactorCorrectionMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished MagneticFormFactorCorrectionMD for {ws_name}")
        self.algorithms_observers.remove(alg)
        self.algorithm_running = False

    def apply_debye_waller_factor_correction_finished(
        self,
        ws_name: str,
        alg: "DebyeWallerFactorCorrectionMDObserver",
        error: bool = False,
        msg="",
    ) -> None:
        """Call when DebyeWallerFactorCorrectionMD finishes.

        Parameters
        ----------
        ws_name : str
            Workspace name
        alg : DebyeWallerFactorCorrectionMDObserver
            Observer
        error : bool, optional
            Error flag, by default False
        msg : str, optional
            Error message, by default ""

        Returns
        -------
        None
        """
        if error:
            logger.error(f"Error in DebyeWallerFactorCorrectionMD for {ws_name}")
            if self.error_callback:
                self.error_callback(msg)
        else:
            logger.information(f"Finished DebyeWallerFactorCorrectionMD for {ws_name}")
        self.algorithms_observers.remove(alg)
        self.algorithm_running = False

    def get_ws_alg_histories(self, ws_name: str) -> list:
        """Get algorithm histories of the workspace.

        Parameters
        ----------
        ws_name : str
            Workspace name

        Returns
        -------
        list
            List of algorithm histories
        """
        if mtd.doesExist(ws_name):
            return mtd[ws_name].getHistory().getAlgorithmHistories()
        return []

    def has_apply_detailed_balance(self, ws_name: str) -> Tuple[bool, str]:
        """Check if the workspace has ApplyDetailedBalanceMD applied.

        Parameters
        ----------
        ws_name : str
            Workspace name

        Returns
        -------
        Tuple[bool, str]
            True if the workspace has ApplyDetailedBalanceMD applied
            Temperature if the workspace has ApplyDetailedBalanceMD applied
        """
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "ApplyDetailedBalanceMD":
                return True, alg_history.getPropertyValue("Temperature")
        return False, ""

    def has_scattered_transmission_correction(self, ws_name: str) -> bool:
        """Check if the workspace has DgsScatteredTransmissionCorrectionMD applied.

        Parameters
        ----------
        ws_name : str
            Workspace name

        Returns
        -------
        bool
            True if the workspace has DgsScatteredTransmissionCorrectionMD applied.
        """
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "DgsScatteredTransmissionCorrectionMD":
                return True
        return False

    def has_magnetic_form_factor_correction(self, ws_name: str) -> Tuple[bool, str]:
        """Check if the workspace has MagneticFormFactorCorrectionMD applied.

        Parameters
        ----------
        ws_name : str
            Workspace name

        Returns
        -------
        Tuple[bool, str]
            True if the workspace has MagneticFormFactorCorrectionMD applied.
            Ion name if the workspace has MagneticFormFactorCorrectionMD applied.
        """
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "MagneticFormFactorCorrectionMD":
                return True, alg_history.getPropertyValue("IonName")
        return False, ""

    def has_debye_waller_factor_correction(self, ws_name: str) -> Tuple[bool, str]:
        """Check if the workspace has DebyeWallerFactorCorrectionMD applied.

        Parameters
        ----------
        ws_name : str
            Workspace name

        Returns
        -------
        Tuple[bool, str]
            True if the workspace has DebyeWallerFactorCorrectionMD applied.
            Ion name if the workspace has DebyeWallerFactorCorrectionMD applied.
        """
        alg_histories = self.get_ws_alg_histories(ws_name)
        for alg_history in alg_histories:
            if alg_history.name() == "DebyeWallerFactorCorrectionMD":
                return True, alg_history.getPropertyValue("MeanSquaredDisplacement")
        return False, ""


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


class MagneticFormFactorCorrectionMDObserver(AlgorithmObserver):
    """Observer for MagneticFormFactorCorrectionMD algorithm"""

    def __init__(self, parent, ws_name: str) -> None:
        super().__init__()
        self.parent = parent
        self.ws_name = ws_name

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call upon algorithm finishing"""
        self.parent.apply_magnetic_form_factor_correction_finished(ws_name=self.ws_name, alg=self, error=False, msg="")

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call upon algorithm error"""
        self.parent.apply_magnetic_form_factor_correction_finished(ws_name=self.ws_name, alg=self, error=True, msg=msg)


class DebyeWallerFactorCorrectionMDObserver(AlgorithmObserver):
    """Observer for DebyeWallerFactorCorrectionMD algorithm"""

    def __init__(self, parent, ws_name: str) -> None:
        super().__init__()
        self.parent = parent
        self.ws_name = ws_name

    def finishHandle(self):  # pylint: disable=invalid-name
        """Call upon algorithm finishing"""
        self.parent.apply_debye_waller_factor_correction_finished(ws_name=self.ws_name, alg=self, error=False, msg="")

    def errorHandle(self, msg):  # pylint: disable=invalid-name
        """Call upon algorithm error"""
        self.parent.apply_debye_waller_factor_correction_finished(ws_name=self.ws_name, alg=self, error=True, msg=msg)


def get_ions_list():
    """Get the list of allowed ions from the MagneticFormFactorCorrectionMD algorithm"""
    try:
        alg = AlgorithmManager.create("MagneticFormFactorCorrectionMD")
    except RuntimeError as err:
        logger.error(str(err))
        return []
    alg.initialize()
    return sorted(alg.getProperty("IonName").allowedValues)
