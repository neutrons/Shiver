"""The Shiver MakeSlice mantid algorithm"""

from mantid.api import DataProcessorAlgorithm, AlgorithmFactory  # pylint: disable=no-name-in-module


class MakeSlice(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeSlice algorithm"""

    def name(self):
        return "MakeSlice"

    def category(self):
        return "Shiver"

    def PyInit(self):
        pass

    def PyExec(self):
        pass


AlgorithmFactory.subscribe(MakeSlice)
