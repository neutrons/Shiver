"""Model for the Histogram tab"""

from mantid.geometry import SymmetryOperationFactory
# pylint: disable=too-few-public-methods
class HistogramModel:
    """Histogram model"""

    def __init__(self):
        pass
        
        
    def symmetry_operations(self,symmetry):
        if (len(symmetry) !=0):
            try:
                return True
            except ValueError as err:
                return False
