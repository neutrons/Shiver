"""Tests for the RefineUBModel"""

import numpy as np
import pytest
from mantid.simpleapi import (  # pylint: disable=no-name-in-module,wrong-import-order
    BinMD,
    CreateMDWorkspace,
    CreateSampleWorkspace,
    FakeMDEventData,
    SetUB,
)

from shiver.models.generate import gather_mde_config_dict, save_mde_config_dict
from shiver.models.refine_ub import RefineUBModel


def test_refine_ub_model():
    """test the RefineUBModel"""
    expt_info = CreateSampleWorkspace()
    SetUB(expt_info)

    mde = CreateMDWorkspace(
        Dimensions=4,
        Extents="-10,10,-10,10,-10,10,-10,10",
        Names="x,y,z,DeltaE",
        Units="r.l.u.,r.l.u.,r.l.u.,DeltaE",
        Frames="QSample,QSample,QSample,General Frame",
    )
    mde.addExperimentInfo(expt_info)
    FakeMDEventData(mde, PeakParams="1e+05,6.283,0,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mde, PeakParams="1e+05,0,6.283,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mde, PeakParams="1e+05,0,0,6.283,0,0.02", RandomSeed="3873875")

    mdh = CreateMDWorkspace(
        Dimensions=4,
        Extents="-5,5,-5,5,-5,5,-10,10",
        Names="[H,0,0],[0,K,0],[0,0,L],DeltaE",
        Units="r.l.u.,r.l.u.,r.l.u.,DeltaE",
        Frames="HKL,HKL,HKL,General Frame",
    )
    mdh.addExperimentInfo(expt_info)
    FakeMDEventData(mdh, PeakParams="1e+05,1,0,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,1,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,0,1,0,0.02", RandomSeed="3873875")
    mdh.getExperimentInfo(0).run().addProperty("W_MATRIX", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0], True)

    mdh = BinMD(
        mdh,
        AlignedDim0="[H,0,0],-2,2,50",
        AlignedDim1="[0,K,0],-2,2,50",
        AlignedDim2="[0,0,L],-2,2,50",
        AlignedDim3="DeltaE,-1.25,1.25,1",
    )

    model = RefineUBModel("mdh", "mde")

    assert model.peaks.name() == "__shiver_peaks"
    assert model.peaks.getNumberPeaks() == 0

    model.predict_peaks()
    assert model.peaks.getNumberPeaks() == 6

    centers, slice1, slice2, slice3 = model.get_perpendicular_slices(3)

    assert centers[0] == (0, 0)
    assert centers[1] == (0, 1)
    assert centers[2] == (0, 1)

    assert slice1 is not None

    assert len(slice1.getNonIntegratedDimensions()) == 2

    assert slice1.getDimension(0).getNBins() == 14
    assert slice1.getDimension(1).getNBins() == 14
    assert slice1.getDimension(2).getNBins() == 1
    assert slice1.getDimension(3).getNBins() == 1
    assert slice1.getSignalArray().min() == 0
    assert slice1.getSignalArray().max() == 25085

    assert slice2 is not None

    assert len(slice2.getNonIntegratedDimensions()) == 2

    assert slice2.getDimension(0).getNBins() == 14
    assert slice2.getDimension(1).getNBins() == 1
    assert slice2.getDimension(2).getNBins() == 13
    assert slice2.getDimension(3).getNBins() == 1
    assert slice2.getSignalArray().min() == 0
    assert slice2.getSignalArray().max() == 25085

    assert slice3 is not None

    assert len(slice1.getNonIntegratedDimensions()) == 2

    assert slice3.getDimension(0).getNBins() == 1
    assert slice3.getDimension(1).getNBins() == 14
    assert slice3.getDimension(2).getNBins() == 13
    assert slice3.getDimension(3).getNBins() == 1
    assert slice3.getSignalArray().min() == 0
    assert slice3.getSignalArray().max() == 25049

    # check peak table model

    peak_table_model = model.get_peaks_table_model()

    assert peak_table_model.mde.getNumDims() == 3

    peak_table_model.set_peak_number_to_rows()
    peaks_subset = peak_table_model.get_peaks_from_rows([0, 1, 4])
    assert peaks_subset.getNumberPeaks() == 3
    assert peaks_subset.getPeak(0).getPeakNumber() == 0
    assert peaks_subset.getPeak(1).getPeakNumber() == 1
    assert peaks_subset.getPeak(2).getPeakNumber() == 4

    # recenter peaks
    peak0_qsample = peak_table_model.ws.getPeak(0).getQSampleFrame()
    peak4_qsample = peak_table_model.ws.getPeak(4).getQSampleFrame()
    peak_table_model.recenter_rows([0, 4])

    # peak 0 should not change since we did put a fake peak there
    assert peak_table_model.ws.getPeak(0).getQSampleFrame() == peak0_qsample

    # peak 4 should change slightly to make the fake peak
    q_sample = peak_table_model.ws.getPeak(4).getQSampleFrame()
    assert q_sample != peak4_qsample

    assert q_sample.getX() == pytest.approx(6.28517246)
    assert q_sample.getY() == pytest.approx(-1.35850032e-05)
    assert q_sample.getZ() == pytest.approx(-2.60902434e-05)

    # refine orientation only, should not change the lattice parameters, only u and v vectors
    peak_table_model.ws.sample().getOrientedLattice().setUFromVectors([1, 0, 0], [0, 1, 0.1])
    assert peak_table_model.ws.sample().getOrientedLattice().a() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().b() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().c() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().alpha() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().beta() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().gamma() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().getuVector() == pytest.approx([1, 0, 0])
    assert peak_table_model.ws.sample().getOrientedLattice().getvVector() == pytest.approx([0, 0.99503719, 0.099503719])

    peak_table_model.refine_orientation([3, 4, 5])
    assert peak_table_model.ws.sample().getOrientedLattice().a() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().b() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().c() == 1
    assert peak_table_model.ws.sample().getOrientedLattice().alpha() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().beta() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().gamma() == 90
    assert peak_table_model.ws.sample().getOrientedLattice().getuVector() == pytest.approx([1, 0, 0])
    assert peak_table_model.ws.sample().getOrientedLattice().getvVector() == pytest.approx([0, 1, 0])

    # refine, should change the lattice parameters and u/v vectors

    peak_table_model.refine([3, 4, 5], "")

    assert peak_table_model.ws.sample().getOrientedLattice().a() == pytest.approx(1)
    assert peak_table_model.ws.sample().getOrientedLattice().b() == pytest.approx(0.99968383)
    assert peak_table_model.ws.sample().getOrientedLattice().c() == pytest.approx(1)
    assert peak_table_model.ws.sample().getOrientedLattice().alpha() == pytest.approx(89.99987616)
    assert peak_table_model.ws.sample().getOrientedLattice().beta() == pytest.approx(90)
    assert peak_table_model.ws.sample().getOrientedLattice().gamma() == pytest.approx(89.99976216)
    assert peak_table_model.ws.sample().getOrientedLattice().getuVector() == pytest.approx([1, 0, 0])
    assert peak_table_model.ws.sample().getOrientedLattice().getvVector() == pytest.approx(
        [4.15107836e-06, 0.99968383, 2.16143683e-06]
    )

    # refine with "Cubic" lattice type
    peak_table_model.refine([3, 4, 5], "Cubic")

    assert peak_table_model.ws.sample().getOrientedLattice().a() == pytest.approx(1)
    assert peak_table_model.ws.sample().getOrientedLattice().b() == pytest.approx(1)
    assert peak_table_model.ws.sample().getOrientedLattice().c() == pytest.approx(1)
    assert peak_table_model.ws.sample().getOrientedLattice().alpha() == pytest.approx(90)
    assert peak_table_model.ws.sample().getOrientedLattice().beta() == pytest.approx(90)
    assert peak_table_model.ws.sample().getOrientedLattice().gamma() == pytest.approx(90)
    assert peak_table_model.ws.sample().getOrientedLattice().getuVector() == pytest.approx([1, 0, 0])
    assert peak_table_model.ws.sample().getOrientedLattice().getvVector() == pytest.approx([0, 1, 0])


def test_mdeconfig_refine_ub():
    """test the mdeconfig in RefineUBModel"""

    expt_info = CreateSampleWorkspace()
    SetUB(expt_info)

    mde = CreateMDWorkspace(
        Dimensions=4,
        Extents="-10,10,-10,10,-10,10,-10,10",
        Names="x,y,z,DeltaE",
        Units="r.l.u.,r.l.u.,r.l.u.,DeltaE",
        Frames="QSample,QSample,QSample,General Frame",
    )
    mde.addExperimentInfo(expt_info)
    FakeMDEventData(mde, PeakParams="1e+05,6.283,0,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mde, PeakParams="1e+05,0,6.283,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mde, PeakParams="1e+05,0,0,6.283,0,0.02", RandomSeed="3873875")

    # add new MDEConfig
    new_mde_config = {}
    new_mde_config["mde_name"] = mde.name()
    new_mde_config["output_dir"] = "/test/file/path"
    new_mde_config["mde_type"] = "Data"
    save_mde_config_dict(mde.name(), new_mde_config)
    # check the mde config values
    mde_config = gather_mde_config_dict(mde.name())

    assert len(mde_config) == 3

    mdh = CreateMDWorkspace(
        Dimensions=4,
        Extents="-5,5,-5,5,-5,5,-10,10",
        Names="[H,0,0],[0,K,0],[0,0,L],DeltaE",
        Units="r.l.u.,r.l.u.,r.l.u.,DeltaE",
        Frames="HKL,HKL,HKL,General Frame",
    )
    mdh.addExperimentInfo(expt_info)
    SetUB(mdh)
    FakeMDEventData(mdh, PeakParams="1e+05,1,0,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,1,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,0,1,0,0.02", RandomSeed="3873875")
    mdh.getExperimentInfo(0).run().addProperty("W_MATRIX", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0], True)

    mdh = BinMD(
        mdh,
        AlignedDim0="[H,0,0],-2,2,50",
        AlignedDim1="[0,K,0],-2,2,50",
        AlignedDim2="[0,0,L],-2,2,50",
        AlignedDim3="DeltaE,-1.25,1.25,1",
    )

    model = RefineUBModel("mdh", "mde")
    model.predict_peaks()

    # peak table model
    peak_table_model = model.get_peaks_table_model()
    peak_table_model.set_peak_number_to_rows()

    # recenter peaks
    peak_table_model.recenter_rows([0, 4])

    # refine, should change the lattice parameters and u/v vectors
    peak_table_model.refine([3, 4, 5], "")
    model.update_mde_with_new_ub()
    # check the oriented lattice
    mde_oriented_lattice = mde.getExperimentInfo(0).sample().getOrientedLattice()
    peak_oriented_lattice = peak_table_model.ws.sample().getOrientedLattice()

    assert peak_oriented_lattice.a() == mde_oriented_lattice.a()
    assert peak_oriented_lattice.b() == mde_oriented_lattice.b()
    assert peak_oriented_lattice.c() == mde_oriented_lattice.c()
    assert peak_oriented_lattice.alpha() == mde_oriented_lattice.alpha()
    assert peak_oriented_lattice.beta() == mde_oriented_lattice.beta()
    assert peak_oriented_lattice.gamma() == mde_oriented_lattice.gamma()
    assert peak_oriented_lattice.getuVector() == pytest.approx(mde_oriented_lattice.getuVector())
    assert peak_oriented_lattice.getvVector() == pytest.approx(mde_oriented_lattice.getvVector())

    # check the mde config values
    mde_config = gather_mde_config_dict(mde.name())

    assert len(mde_config) == 4
    assert "SampleParameters" in mde_config
    assert mde_config["SampleParameters"]["a"] == mde_oriented_lattice.a()
    assert mde_config["SampleParameters"]["b"] == mde_oriented_lattice.b()
    assert mde_config["SampleParameters"]["c"] == mde_oriented_lattice.c()
    assert mde_config["SampleParameters"]["alpha"] == mde_oriented_lattice.alpha()
    assert mde_config["SampleParameters"]["beta"] == mde_oriented_lattice.beta()
    assert mde_config["SampleParameters"]["gamma"] == mde_oriented_lattice.gamma()

    u_array = np.array(mde_config["SampleParameters"]["u"].split(","), dtype=float)
    assert u_array == pytest.approx(mde_oriented_lattice.getuVector())
    v_array = np.array(mde_config["SampleParameters"]["v"].split(","), dtype=float)
    assert v_array == pytest.approx(mde_oriented_lattice.getvVector())
