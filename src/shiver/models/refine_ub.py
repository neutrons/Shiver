from mantidqt.widgets.workspacedisplay.table.model import TableWorkspaceDisplayModel
from mantid.simpleapi import CreatePeaksWorkspace, CentroidPeaksMD, SliceMD, IndexPeaks, CopySample, PredictPeaks


class PeaksTableWorkspaceDisplayModel(TableWorkspaceDisplayModel):
    def __init__(self, peaks, mde):
        super().__init__(peaks)
        self.set_parent_mde(mde)

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
            OutputWorkspace="__mde_sliced",
        )

        self.mde = mde

    def get_peaks_from_rows(self, rows):
        peaks_subset = CreatePeaksWorkspace(InstrumentWorkspace=self.ws, NumberOfPeaks=0, OutputType="LeanElasticPeak")

        for row in rows:
            peaks_subset.addPeak(self.ws.getPeak(row))

        return peaks_subset

    def set_peak_number_to_rows(self):
        for row in range(self.ws.getNumberPeaks()):
            self.ws.getPeak(row).setPeakNumber(row)

    def recenter_rows(self, rows):
        print("recenter_rows", rows)
        self.set_peak_number_to_rows()
        subset = self.get_peaks_from_rows(rows)

        subset = CentroidPeaksMD(InputWorkspace=self.mde, PeaksWorkspace=subset, PeakRadius=0.1)
        IndexPeaks(subset, RoundHKLs=False, Tolerance=0.5)
        self.update_peaks(subset)

    def update_peaks(self, updated_peaks):
        for n in range(updated_peaks.getNumberPeaks()):
            new_peak = updated_peaks.getPeak(n)
            old_peak = self.ws.getPeak(new_peak.getPeakNumber())
            print("Recentering peak", new_peak.getPeakNumber())
            print("Qsample", old_peak.getQSampleFrame(), "-->", new_peak.getQSampleFrame())
            old_peak.setQSampleFrame(new_peak.getQSampleFrame())
            print("HKL", old_peak.getHKL(), "-->", new_peak.getHKL())
            old_peak.setHKL(*new_peak.getHKL())

    def set_peaks(self, peaks):
        self.ws = peaks


class RefineUBModel:
    def __init__(self, mdh, mde):
        self.set_workspace(mdh)
        self.mde = mde

    def recenter(self):
        print("recenter")
        self.peaks_table.model.recenter_rows(self.peaks_table.view.model().recenter_rows())

    def set_workspace(self, mdh):
        self.mdh = mdh

        try:
            CopySample(self.mdh, self.peaks)
            IndexPeaks(self.peaks, RoundHKL=False)
        except (NameError, AttributeError):
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
