from qtpy.QtWidgets import QApplication
import shiver.models.makeslice  # noqa
from shiver.presenters.refine_ub import RefineUB
from mantid.simpleapi import (
    LoadMD,
    MakeSlice,
)

mde = LoadMD("/home/nxw/src/Shiver/tests/data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs")
Ei = mde.getExperimentInfo(0).run()["Ei"].value
mdh = MakeSlice(
    mde,
    Dimension0Binning="-1,0.02,2",
    Dimension1Binning="-1,0.02,2",
    Dimension2Binning="-1,0.02,3",
    Dimension3Name="DeltaE",
    Dimension3Binning=f"{-Ei*0.05},{Ei*0.05}",
)


app = QApplication([])
window = RefineUB(str(mdh), str(mde))
window.view.show()
app.exec_()
