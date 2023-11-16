import numpy as np
import math
from mantidqt.widgets.workspacedisplay.table.model import TableWorkspaceDisplayModel
from mantid.simpleapi import (
    CreatePeaksWorkspace,
    CentroidPeaksMD,
    SliceMD,
    IndexPeaks,
    CopySample,
    PredictPeaks,
    mtd,
    CalculateUMatrix,
    FindUBUsingIndexedPeaks,
    SelectCellOfType,
    SetUB,
    SliceMDHisto,
)
from mantid.kernel import Logger

logger = Logger("SHIVER")


class PeaksTableWorkspaceDisplayModel(TableWorkspaceDisplayModel):
    def __init__(self, peaks, mde):
        super().__init__(peaks)
        self.set_parent_mde(mde)
        self.error_callback = None
        self.origonal_ub = self.ws.sample().getOrientedLattice().getUB().copy()

    def set_parent_mde(self, mde):
        # Drop the DeltaE dimension
        d0 = mde.getDimension(0)
        d1 = mde.getDimension(1)
        d2 = mde.getDimension(2)
        mde = SliceMD(
            mde,
            AlignedDim0=f"{d0.name},{d0.getMinimum()},{d0.getMaximum()},{d0.getNBins()}",
            AlignedDim1=f"{d1.name},{d1.getMinimum()},{d1.getMaximum()},{d1.getNBins()}",
            AlignedDim2=f"{d2.name},{d2.getMinimum()},{d2.getMaximum()},{d2.getNBins()}",
            StoreInADS=False,
        )

        self.mde = mde

    def get_peaks_from_rows(self, rows):
        peaks_subset = CreatePeaksWorkspace(
            InstrumentWorkspace=self.ws, NumberOfPeaks=0, OutputType="LeanElasticPeak", OutputWorkspace="__peaks_subset"
        )

        for row in rows:
            peaks_subset.addPeak(self.ws.getPeak(row))

        return peaks_subset

    def set_peak_number_to_rows(self):
        for row in range(self.ws.getNumberPeaks()):
            self.ws.getPeak(row).setPeakNumber(row)

    def recenter_rows(self, rows):
        self.set_peak_number_to_rows()
        subset = self.get_peaks_from_rows(rows)

        CentroidPeaksMD(InputWorkspace=self.mde, PeaksWorkspace=subset, PeakRadius=0.1, OutputWorkspace=subset)
        IndexPeaks(subset, RoundHKLs=False, Tolerance=0.5)

        for n in range(subset.getNumberPeaks()):
            new_peak = subset.getPeak(n)
            old_peak = self.ws.getPeak(new_peak.getPeakNumber())
            logger.information(
                "Recentering Peak {}, Qsample moved from {} to {}, HKL moved from {} to {}".format(
                    new_peak.getPeakNumber(),
                    old_peak.getQSampleFrame(),
                    new_peak.getQSampleFrame(),
                    old_peak.getHKL(),
                    new_peak.getHKL(),
                )
            )
            old_peak.setQSampleFrame(new_peak.getQSampleFrame())
            old_peak.setHKL(*new_peak.getHKL())

        subset.delete()

    def set_peaks(self, peaks):
        self.ws = peaks

    def get_lattice_parameters(self):
        lattice = {}
        ol = self.ws.sample().getOrientedLattice()
        lattice["a"] = ol.a()
        lattice["b"] = ol.b()
        lattice["c"] = ol.c()
        lattice["alpha"] = ol.alpha()
        lattice["beta"] = ol.beta()
        lattice["gamma"] = ol.gamma()
        return lattice

    def update_ub(self, ws):
        CopySample(ws, self.ws, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)
        IndexPeaks(self.ws, RoundHKLs=False, Tolerance=0.5)

    def refine_orientation(self, rows):
        subset = self.get_peaks_from_rows(rows)
        try:
            CalculateUMatrix(subset, **self.get_lattice_parameters())
        except (RuntimeError, ValueError) as e:
            logger.error(str(e))
            if self.error_callback:
                self.error_callback(str(e))
            raise
        self.update_ub(subset)
        subset.delete()

    def refine(self, rows, lattice_type):
        subset = self.get_peaks_from_rows(rows)
        try:
            FindUBUsingIndexedPeaks(subset)
            if lattice_type:
                SelectCellOfType(subset, CellType=lattice_type, Apply=True)
        except (RuntimeError, ValueError) as e:
            logger.error(str(e))
            if self.error_callback:
                self.error_callback(str(e))
            raise
        self.update_ub(subset)
        subset.delete()

    def undo(self):
        current_ub = self.ws.sample().getOrientedLattice().getUB()
        if np.array_equal(self.origonal_ub, current_ub):
            return False
        SetUB(self.ws, UB=self.origonal_ub)
        IndexPeaks(self.ws, RoundHKLs=False, Tolerance=0.5)
        return True

    def connect_error_message(self, callback):
        self.error_callback = callback


class RefineUBModel:
    def __init__(self, mdh, mde):
        self.set_workspace(mdh)
        self.mde = mtd[mde]

    def update_workspaces(self, mdh, mde):
        self.mde = mtd[mde]
        self.mdh = mtd[mdh]
        self.peaks_table.set_parent_mde(self.mde)

    def recenter(self):
        self.peaks_table.model.recenter_rows(self.peaks_table.view.model().recenter_rows())

    def set_workspace(self, mdh):
        self.mdh = mtd[mdh]

        self.peaks = CreatePeaksWorkspace(
            InstrumentWorkspace=self.mdh,
            OutputType="LeanElasticPeak",
            NumberOfPeaks=0,
            OutputWorkspace=self.get_peaks_ws_name(),
        )

    def get_mdh(self):
        return self.mdh

    def get_peaks_ws(self):
        return self.peaks

    def get_peaks_ws_name(self):
        return "__shiver_peaks"

    def get_PeaksTableWorkspaceDisplayModel(self):
        self.peaks_table = PeaksTableWorkspaceDisplayModel(self.get_peaks_ws(), self.mde)
        return self.peaks_table

    def predict_peaks(self):
        self.peaks = PredictPeaks(self.mdh, OutputType="LeanElasticPeak", OutputWorkspace=self.get_peaks_ws_name())
        self.peaks_table.set_peaks(self.peaks)

    def update_mde_with_new_ub(self):
        CopySample(self.peaks, self.mde, CopyName=False, CopyMaterial=False, CopyEnvironment=False, CopyShape=False)

    def get_perpendicular_slices(self, peak_row):
        W_MATRIX = np.array(self.mdh.getExperimentInfo(0).run().get("W_MATRIX").value, dtype=float).reshape(3, 3)
        xyz = np.linalg.inv(W_MATRIX).dot(self.peaks.getPeak(peak_row).getHKL())

        start = []
        center = []
        end = []
        for d in range(3):
            dim = self.mdh.getDimension(d)
            cen = (xyz[d] - dim.getMinimum()) / dim.getBinWidth()
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
        except (RuntimeError, ValueError) as e:
            logger.error(str(e))
            slice1 = None

        try:
            slice2 = SliceMDHisto(
                self.mdh,
                Start=[start[0], center[1], start[2], 0],
                End=[end[0], center[1] + 1, end[2], 1],
                StoreInADS=False,
            )
        except (RuntimeError, ValueError) as e:
            logger.error(str(e))
            slice2 = None

        try:
            slice3 = SliceMDHisto(
                self.mdh,
                Start=[center[0], start[1], start[2], 0],
                End=[center[0] + 1, end[1], end[2], 1],
                StoreInADS=False,
            )
        except (RuntimeError, ValueError) as e:
            logger.error(str(e))
            slice3 = None

        return slice1, slice2, slice3

    def connect_error_message(self, callback):
        self.error_callback = callback
        self.peaks_table.connect_error_message(callback)
