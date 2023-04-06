"""UI tests for Sample Parameters dialog"""
import functools
from qtpy import QtCore, QtWidgets
from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver.views.sample import SampleView, LatticeParametersWidget, SampleDialog
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel

import os
import re

#python unittest mock qfileDialog in
#invalid a- > load ub -> a background color should be valid


