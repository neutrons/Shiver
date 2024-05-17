"""UI test for Refine UB widget"""
import pytest
from qtpy import QtCore
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    CreateMDWorkspace,
    SetUB,
    FakeMDEventData,
    BinMD,
    CreateSampleWorkspace,
)
from shiver.presenters.refine_ub import RefineUB


def test_refine_ub_ui(qtbot):
    """Test the UI for Refine UB"""
    mde = CreateMDWorkspace(
        Dimensions=4,
        Extents="-10,10,-10,10,-10,10,-10,10",
        Names="x,y,z,DeltaE",
        Units="r.l.u.,r.l.u.,r.l.u.,DeltaE",
        Frames="QSample,QSample,QSample,General Frame",
    )
    expt_info = CreateSampleWorkspace()
    mde.addExperimentInfo(expt_info)
    SetUB(mde)
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
    SetUB(mdh)
    FakeMDEventData(mdh, PeakParams="1e+05,1,0,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,1,0,0,0.02", RandomSeed="3873875")
    FakeMDEventData(mdh, PeakParams="1e+05,0,0,1,0,0.02", RandomSeed="3873875")
    mdh.getExperimentInfo(0).run().addProperty("W_MATRIX", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0], True)

    mdh = BinMD(
        mdh,
        AlignedDim0="[H,0,0],-2,2,10",
        AlignedDim1="[0,K,0],-2,2,10",
        AlignedDim2="[0,0,L],-2,2,10",
        AlignedDim3="DeltaE,-1.25,1.25,1",
    )

    refine_ub = RefineUB("mdh", "mde")
    qtbot.addWidget(refine_ub.view)
    refine_ub.view.show()
    assert refine_ub.view.isVisible()
    assert refine_ub.view.lattice_a.text() == "1.0"
    assert refine_ub.view.lattice_b.text() == "1.0"
    assert refine_ub.view.lattice_c.text() == "1.0"
    assert refine_ub.view.lattice_alpha.text() == "90.0"
    assert refine_ub.view.lattice_beta.text() == "90.0"
    assert refine_ub.view.lattice_gamma.text() == "90.0"

    qtbot.mouseClick(refine_ub.view.predict_peaks, QtCore.Qt.LeftButton)
    qtbot.wait(100)

    # select a row to plot
    qtbot.mouseClick(
        refine_ub.view.peaks_table.view.viewport(),
        QtCore.Qt.LeftButton,
        pos=QtCore.QPoint(
            refine_ub.view.peaks_table.view.columnViewportPosition(3),
            refine_ub.view.peaks_table.view.rowViewportPosition(4),
        ),
    )

    qtbot.wait(100)

    # check 3 plots axes set correctly
    assert refine_ub.view.axes[0].get_xlabel() == "[H,0,0] (r.l.u.)"
    assert refine_ub.view.axes[0].get_xlim() == pytest.approx((-0.8, 0.8))
    assert refine_ub.view.axes[0].get_ylabel() == "[0,K,0] (r.l.u.)"
    assert refine_ub.view.axes[0].get_ylim() == pytest.approx((0.4, 1.6))

    assert refine_ub.view.axes[1].get_xlabel() == "[H,0,0] (r.l.u.)"
    assert refine_ub.view.axes[1].get_xlim() == pytest.approx((-0.8, 0.8))
    assert refine_ub.view.axes[1].get_ylabel() == "[0,0,L] (r.l.u.)"
    assert refine_ub.view.axes[1].get_ylim() == pytest.approx((-0.8, 0.8))

    assert refine_ub.view.axes[2].get_xlabel() == "[0,K,0] (r.l.u.)"
    assert refine_ub.view.axes[2].get_xlim() == pytest.approx((0.4, 1.6))
    assert refine_ub.view.axes[2].get_ylabel() == "[0,0,L] (r.l.u.)"
    assert refine_ub.view.axes[2].get_ylim() == pytest.approx((-0.8, 0.8))

    # select 1 peaks then press "Recenter" and check that UB is updated
    assert refine_ub.model.peaks.getPeak(3).getQSampleFrame() == pytest.approx([0, 6.28318531, 0])

    qtbot.mouseClick(
        refine_ub.view.peaks_table.view.viewport(),
        QtCore.Qt.LeftButton,
        pos=QtCore.QPoint(60, refine_ub.view.peaks_table.view.rowViewportPosition(3) + 20),
    )
    qtbot.wait(100)

    assert refine_ub.view.peaks_table.view.model().recenter_rows() == [3]

    qtbot.mouseClick(refine_ub.view.recenter_peaks, QtCore.Qt.LeftButton)

    assert refine_ub.model.peaks.getPeak(3).getQSampleFrame() == pytest.approx(
        [5.00797398e-07, 6.28529930, -2.60952093e-05]
    )

    # test round HKL button
    assert refine_ub.model.peaks.getPeak(3).getHKL() == pytest.approx([-4.15318e-06, 7.97044e-08, 1.000336])
    qtbot.mouseClick(refine_ub.view.round_hkl, QtCore.Qt.LeftButton)
    assert refine_ub.model.peaks.getPeak(3).getHKL() == pytest.approx([0, 0, 1])

    # test select all/deselect all buttons
    qtbot.mouseClick(refine_ub.view.select_all, QtCore.Qt.LeftButton)
    assert refine_ub.view.peaks_table.view.model().refine_rows() == [0, 1, 2, 3, 4, 5]
    qtbot.mouseClick(refine_ub.view.deselect_all, QtCore.Qt.LeftButton)
    assert refine_ub.view.peaks_table.view.model().refine_rows() == []

    # select 3 peaks then press "Refine" and check that UB is updated
    assert refine_ub.model.peaks.sample().getOrientedLattice().a() == 1
    assert refine_ub.model.peaks.sample().getOrientedLattice().b() == 1
    assert refine_ub.model.peaks.sample().getOrientedLattice().c() == 1
    assert refine_ub.model.peaks.sample().getOrientedLattice().alpha() == 90
    assert refine_ub.model.peaks.sample().getOrientedLattice().beta() == 90
    assert refine_ub.model.peaks.sample().getOrientedLattice().gamma() == 90

    qtbot.mouseClick(
        refine_ub.view.peaks_table.view.viewport(),
        QtCore.Qt.LeftButton,
        pos=QtCore.QPoint(15, refine_ub.view.peaks_table.view.rowViewportPosition(3) + 20),
    )
    qtbot.mouseClick(
        refine_ub.view.peaks_table.view.viewport(),
        QtCore.Qt.LeftButton,
        pos=QtCore.QPoint(15, refine_ub.view.peaks_table.view.rowViewportPosition(4) + 20),
    )
    qtbot.mouseClick(
        refine_ub.view.peaks_table.view.viewport(),
        QtCore.Qt.LeftButton,
        pos=QtCore.QPoint(15, refine_ub.view.peaks_table.view.rowViewportPosition(5) + 20),
    )
    qtbot.wait(100)

    assert refine_ub.view.peaks_table.view.model().refine_rows() == [3, 4, 5]

    qtbot.mouseClick(refine_ub.view.refine_btn, QtCore.Qt.LeftButton)

    qtbot.wait(1000)
    assert refine_ub.model.peaks.sample().getOrientedLattice().a() == pytest.approx(1)
    assert refine_ub.model.peaks.sample().getOrientedLattice().b() == pytest.approx(1)
    assert refine_ub.model.peaks.sample().getOrientedLattice().c() == pytest.approx(0.99966366)
    assert refine_ub.model.peaks.sample().getOrientedLattice().alpha() == pytest.approx(90)
    assert refine_ub.model.peaks.sample().getOrientedLattice().beta() == pytest.approx(89.99976212)
    assert refine_ub.model.peaks.sample().getOrientedLattice().gamma() == pytest.approx(90)

    # assert
