"""Model for the Histogram tab"""
import os.path
import numpy

# pylint: disable=no-name-in-module
from mantid.simpleapi import mtd, DeleteWorkspace, RenameWorkspace, CreateSingleValuedWorkspace, LoadIsawUB
from mantid.geometry import OrientedLattice
from mantid.kernel import Logger
from mantid.simpleapi import mtd,SetUB, DeleteWorkspace
from mantidqtinterfaces.DGSPlanner.LoadNexusUB import LoadNexusUB
logger = Logger("SHIVER")


class SampleModel:
    """Histogram model"""

    def __init__(self, name):
        self.error_callback = None
        self.name = name

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def get_matrix_ub(self):
        if (mtd.doesExist(self.name) and 'BL14B:CS:UBMatrix' in mtd[self.name].getExperimentInfo(0).run()):
            return mtd[self.name].getExperimentInfo(0).run()['BL14B:CS:UBMatrix'].value[0]
        else:
            return [
            "0.01","0","0",
            "0","0.01","0",
            "0","0","0.01"
            ]
  
    def get_lattice_ub(self):
        if (mtd.doesExist(self.name)):
            return mtd[self.name].getExperimentInfo(0).sample().getOrientedLattice()
        else:
            return False    
            

    def set_ub(self, params):
        """SetUB with mandit"""

        ws = mtd[self.name]
        #some check
        uvec = numpy.array([
            float(params['latt_ux']), 
            float(params['latt_uy']), 
            float(params['latt_uz'])
        ])
        vvec = numpy.array([
            float(params['latt_vx']), 
            float(params['latt_vy']), 
            float(params['latt_vz'])
        ])
        if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
            err_msg = f"Invalid values in u and v\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
        else:        
            SetUB(
                Workspace=ws, 
                a=float(params['latt_a']), 
                b=float(params['latt_b']), 
                c=float(params['latt_c']), 
                alpha=float(params['alpha']), 
                beta=float(params['beta']), 
                gamma=float(params['gamma']),
                u=uvec,
                v=vvec
            )
            print("done!")
            logger.information(f"SetUP completed for {params['name']}")

    def load_nexus_ub(self,filename):
        try:
            __temp_ub = LoadNexusUB(str(filename))
            ol = mantid.geometry.OrientedLattice()
            print("ol before setup",ol)
            ol.setUB(__temp_ub)
            print("ol",ol)
            DeleteWorkspace(__temp_ub)
        except Exception as e:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {e}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)        

    def load_isaw_ub(self,filename):
        try:
            __tempws = CreateSingleValuedWorkspace(0.0)
            LoadIsawUB(__tempws, str(filename))
            ol = OrientedLattice(__tempws.sample().getOrientedLattice())
            ol.setU(__tempws.sample().getOrientedLattice().getU())
            DeleteWorkspace(__tempws)
            return ol
        except Exception as e:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {e}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)        
                
    
    
