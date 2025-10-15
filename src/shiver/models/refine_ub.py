"""Model for the Refine UB widget"""

import math

import numpy as np
from mantid.kernel import Logger
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    CalculateUMatrix,
    CentroidPeaksMD,
    CopySample,
    CreatePeaksWorkspace,
    FindUBUsingIndexedPeaks,
    IndexPeaks,
    OptimizeLatticeForCellType,
    PredictPeaks,
    SetUB,
    SliceMD,
    SliceMDHisto,
    mtd,
)
from mantidqt.widgets.workspacedisplay.table.model import TableWorkspaceDisplayModel

from shiver.models.sample import update_sample_mde_config

logger = Logger("SHIVER")


class PeaksTableWorkspaceDisplayModel(TableWorkspaceDisplayModel):
    """Model for the peaks table"""

    def __init__(self, peaks, mde):
        super().__init__(peaks)
        self.set_parent_mde(mde)
        self.error_callback = None
        self.origonal_ub = self.ws.sample().getOrientedLattice().getUB().copy()

    def set_parent_mde(self, mde):
        """set the MDE used for recentering

        Drop the DeltaE dimension"""
        dim0 = mde.getDimension(0)
        dim1 = mde.getDimension(1)
        dim2 = mde.getDimension(2)
        mde = SliceMD(
            mde,
            AlignedDim0=f"{dim0.name},{dim0.getMinimum()},{dim0.getMaximum()},{dim0.getNBins()}",
            AlignedDim1=f"{dim1.name},{dim1.getMinimum()},{dim1.getMaximum()},{dim1.getNBins()}",
            AlignedDim2=f"{dim2.name},{dim2.getMinimum()},{dim2.getMaximum()},{dim2.getNBins()}",
            StoreInADS=False,
        )

        self.mde = mde

    def get_peaks_from_rows(self, rows):
        """Extract a subset of peaks using the row numbers"""
        peaks_subset = CreatePeaksWorkspace(
            InstrumentWorkspace=self.ws, NumberOfPeaks=0, OutputType="LeanElasticPeak", OutputWorkspace="__peaks_subset"
        )

        for row in rows:
            peaks_subset.addPeak(self.ws.getPeak(row))

        return peaks_subset

    def set_peak_number_to_rows(self):
        """set the peaks numbers to match the rows so that the peaks subset can be match back"""
        for row in range(self.ws.getNumberPeaks()):
            self.ws.getPeak(row).setPeakNumber(row)

    def recenter_rows(self, rows):
        """Recenter the selected peaks"""
        self.set_peak_number_to_rows()
        subset = self.get_peaks_from_rows(rows)

        CentroidPeaksMD(InputWorkspace=self.mde, PeaksWorkspace=subset, PeakRadius=0.25, OutputWorkspace=subset)
        IndexPeaks(subset, RoundHKLs=False, Tolerance=0.5)

        for peak in range(subset.getNumberPeaks()):
            new_peak = subset.getPeak(peak)
            old_peak = self.ws.getPeak(new_peak.getPeakNumber())
            logger.information(
                f"Recentering Peak {new_peak.getPeakNumber()}, "
                f"Qsample moved from {old_peak.getQSampleFrame()} to {new_peak.getQSampleFrame()}, "
                f"HKL moved from {old_peak.getHKL()} to {new_peak.getHKL()}"
            )

            old_peak.setQSampleFrame(new_peak.getQSampleFrame())
            old_peak.setHKL(*new_peak.getHKL())

        subset.delete()

    def set_peaks(self, peaks):
        """Replace the peaks workspace in the models"""
        self.ws = peaks

    def get_lattice_parameters(self):
        """collect and return the lattice parameters from the peaks workspace"""
        lattice = {}
        oriented_lattice = self.ws.sample().getOrientedLattice()
        lattice["a"] = oriented_lattice.a()
        lattice["b"] = oriented_lattice.b()
        lattice["c"] = oriented_lattice.c()
        lattice["alpha"] = oriented_lattice.alpha()
        lattice["beta"] = oriented_lattice.beta()
        lattice["gamma"] = oriented_lattice.gamma()
        return lattice

    def update_ub(self, new_ub):
        """Update the UB of the peaks workspace from the refine workspace"""
        CopySample(new_ub, self.ws, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)

    def refine_orientation(self, rows):
        """Refine the UB orientation only using the selected rows"""
        subset = self.get_peaks_from_rows(rows)
        try:
            CalculateUMatrix(subset, **self.get_lattice_parameters())
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            raise
        self.update_ub(subset)
        subset.delete()

    def refine(self, rows, lattice_type):
        """Refine the UB using the selected rows"""
        subset = self.get_peaks_from_rows(rows)
        try:
            FindUBUsingIndexedPeaks(subset)
            if lattice_type:
                OptimizeLatticeForCellType(subset, CellType=lattice_type, Apply=True)
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            if self.error_callback:
                self.error_callback(str(err))
            raise
        self.update_ub(subset)
        subset.delete()

    def undo(self):
        """Set the origonal UB onto the peaks workspace"""
        current_ub = self.ws.sample().getOrientedLattice().getUB()
        if np.array_equal(self.origonal_ub, current_ub):
            return False
        SetUB(self.ws, UB=self.origonal_ub)
        return True

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback


class RefineUBModel:
    """Model for the refinement UB tab"""

    REFINE_UB_PEAKS_WS_NAME = "__shiver_peaks"

    def __init__(self, mdh, mde):
        self.mde = mtd[mde]
        self.mdh = mtd[mdh]

        self.peaks = CreatePeaksWorkspace(
            InstrumentWorkspace=self.mdh,
            OutputType="LeanElasticPeak",
            NumberOfPeaks=0,
            OutputWorkspace=self.REFINE_UB_PEAKS_WS_NAME,
        )

        self.peaks_table_model = PeaksTableWorkspaceDisplayModel(self.peaks, self.mde)

        self.error_callback = None

    def update_workspaces(self, mdh, mde):
        """Set the MD workspace, after the UB has been refined"""
        self.mde = mtd[mde]
        self.mdh = mtd[mdh]
        self.peaks_table_model.set_parent_mde(self.mde)

    def get_mdh(self):
        """Return the MDHistoWorkspace"""
        return self.mdh

    def get_peaks_table_model(self):
        """get the model for the peaks table"""
        return self.peaks_table_model

    def predict_peaks(self):
        """Run predict peaks, the set new peaks to the peaks table model"""
        self.peaks = PredictPeaks(
            self.mdh,
            OutputType="LeanElasticPeak",
            CalculateWavelength=False,
            OutputWorkspace=self.REFINE_UB_PEAKS_WS_NAME,
        )
        self.peaks_table_model.set_peaks(self.peaks)

    def update_mde_with_new_ub(self):
        """Update the UB in the MDE from the one in the peaks workspace"""
        CopySample(self.peaks, self.mde, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)
        update_sample_mde_config(self.mde.name(), self.mde.getExperimentInfo(0).sample().getOrientedLattice())

    def get_perpendicular_slices(self, peak_row):
        """Create 3 perpendicular slices center on the peaks corresponding to the given row"""
        w_matrix = np.array(self.mdh.getExperimentInfo(0).run().get("W_MATRIX").value, dtype=float).reshape(3, 3)
        xyz = np.linalg.inv(w_matrix).dot(self.peaks.getPeak(peak_row).getHKL())

        start = []
        center = []
        end = []
        for ndim in range(3):
            dim = self.mdh.getDimension(ndim)
            cen = (xyz[ndim] - dim.getMinimum()) / dim.getBinWidth()
            center.append(round(cen))
            half_width = 0.5 / dim.getBinWidth()
            start.append(math.floor((cen - half_width)))
            end.append(math.ceil(cen + half_width))

        try:
            slice1 = SliceMDHisto(
                self.mdh,
                Start=[start[0], start[1], center[2], 0],
                End=[end[0], end[1], center[2] + 1, 1],
                StoreInADS=False,
            )
            if len(slice1.getNonIntegratedDimensions()) != 2:
                raise ValueError("SliceMDHisto didn't result in 2D slice")
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            slice1 = None

        try:
            slice2 = SliceMDHisto(
                self.mdh,
                Start=[start[0], center[1], start[2], 0],
                End=[end[0], center[1] + 1, end[2], 1],
                StoreInADS=False,
            )
            if len(slice2.getNonIntegratedDimensions()) != 2:
                raise ValueError("SliceMDHisto didn't result in 2D slice")
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            slice2 = None

        try:
            slice3 = SliceMDHisto(
                self.mdh,
                Start=[center[0], start[1], start[2], 0],
                End=[center[0] + 1, end[1], end[2], 1],
                StoreInADS=False,
            )
            if len(slice3.getNonIntegratedDimensions()) != 2:
                raise ValueError("SliceMDHisto didn't result in 2D slice")
        except (RuntimeError, ValueError) as err:
            logger.error(str(err))
            slice3 = None

        centers = ((xyz[0], xyz[1]), (xyz[0], xyz[2]), (xyz[1], xyz[2]))

        return centers, slice1, slice2, slice3

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback
        self.peaks_table_model.connect_error_message(callback)
