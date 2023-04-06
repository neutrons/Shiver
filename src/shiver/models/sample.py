"""Model for the Histogram tab"""
import numpy

# pylint: disable=no-name-in-module
from mantid.simpleapi import mtd, DeleteWorkspace, SetUB, CreateSingleValuedWorkspace, LoadIsawUB
from mantid.geometry import OrientedLattice
from mantid.kernel import Logger
from mantidqtinterfaces.DGSPlanner.LoadNexusUB import LoadNexusUB
from mantidqtinterfaces.DGSPlanner.ValidateOL import ValidateUB

logger = Logger("SHIVER")


class SampleModel:
    """Histogram model"""

    def __init__(self, name):
        self.error_callback = None
        self.name = name
        self.ol = None

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    # def get_matrix_ub(self):
    #    # if  'CrystalAlign:UBMatrix' in w.getExperimentInfo(0).run().keys()
    #    matrix = "0.0100,0.0000,0.0000,0.0000,0.0100,0.0000,0.0000,0.0000,0.0100"
    #    if mtd.doesExist(self.name):
    #        matrix_key = ""
    #        for key in mtd[self.name].getExperimentInfo(0).run().keys():
    #            if "CrystalAlign::UBMatrix" in key:  # CrystalAlign:UBMatrix
    #                matrix_key = key
    #                break
    #        if matrix_key:
    #            matrix = mtd[self.name].getExperimentInfo(0).run()[matrix_key].value[0]
    #            return matrix
    #    return matrix

    def get_lattice_ub(self):
        if mtd.doesExist(self.name):
            return mtd[self.name].getExperimentInfo(0).sample().getOrientedLattice()
        else:
            err_msg = f"Workspace {self.name} does not exist\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return False

    def get_UB_data_from_lattice(self, params):
        # u and v cannot be colinear ; see projections crossproduct of u and v
        ub_matrix = []
        uvec = numpy.array([params["latt_ux"], params["latt_uy"], params["latt_uz"]])
        vvec = numpy.array([params["latt_vx"], params["latt_vy"], params["latt_vz"]])
        if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
            err_msg = "uv and vx arrays need to be non co-linear\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return ub_matrix
        else:
            try:
                ol = OrientedLattice(
                    params["latt_a"],
                    params["latt_b"],
                    params["latt_c"],
                    params["latt_alpha"],
                    params["latt_beta"],
                    params["latt_gamma"],
                )
                ol.setUFromVectors(uvec, vvec)
                ub_matrix = ol.getUB()
                self.ol = ol
                print("ub_matrix", ub_matrix)
                return ub_matrix
            except ValueError as value_error:
                err_msg = f"Invalid lattices: {value_error}\n"
                logger.error(err_msg)
                if self.error_callback:
                    self.error_callback(err_msg)
                return ub_matrix

    def get_lattice_from_UB_data(self, ub_matrix):
        ub_matrix = numpy.array(ub_matrix)
        if ValidateUB(ub_matrix):
            ol = OrientedLattice()
            ol.setUB(ub_matrix)
            self.ol = ol
            return ol
        else:
            err_msg = "Invalid values in matrix\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None

    def set_ub(self, params):
        """SetUB with mandit"""

        ws = mtd[self.name]
        # some check
        uvec = numpy.array([float(params["latt_ux"]), float(params["latt_uy"]), float(params["latt_uz"])])
        vvec = numpy.array([float(params["latt_vx"]), float(params["latt_vy"]), float(params["latt_vz"])])
        if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
            err_msg = "Invalid values in u and v\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
        else:
            SetUB(
                Workspace=ws,
                a=float(params["latt_a"]),
                b=float(params["latt_b"]),
                c=float(params["latt_c"]),
                alpha=float(params["alpha"]),
                beta=float(params["beta"]),
                gamma=float(params["gamma"]),
                u=uvec,
                v=vvec,
            )
            logger.information(f"SetUP completed for {params['name']}")

    def load_nexus_ub(self, filename):
        try:
            __temp_ub = LoadNexusUB(str(filename))
            ol = OrientedLattice()
            print("ol before setup", ol)
            ol.setUB(__temp_ub)
            print("ol", ol)
            # example HYS_371495.nxs.h5
            self.ol = ol
            return ol
            # DeleteWorkspace(__temp_ub)
        except Exception as e:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {e}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None

    def load_isaw_ub(self, filename):
        try:
            __tempws = CreateSingleValuedWorkspace(0.0)
            LoadIsawUB(__tempws, str(filename))
            ol = OrientedLattice(__tempws.sample().getOrientedLattice())
            ol.setUB(__tempws.sample().getOrientedLattice().getUB())
            print(ol.getUB())
            DeleteWorkspace(__tempws)
            print(ol.getUB())
            self.ol = ol
            return ol
        except Exception as e:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {e}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None
