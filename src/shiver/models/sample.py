"""Model for the Sample Parameters dialog"""
import numpy

# pylint: disable=no-name-in-module
from mantid.simpleapi import mtd, DeleteWorkspace, SetUB, CreateSingleValuedWorkspace, LoadIsawUB, LoadNexusProcessed
from mantid.geometry import OrientedLattice
from mantid.kernel import Logger
from mantidqtinterfaces.DGSPlanner.LoadNexusUB import LoadNexusUB
from mantidqtinterfaces.DGSPlanner.ValidateOL import ValidateUB

logger = Logger("SHIVER")


class SampleModel:
    """Sample model"""

    def __init__(self, name=None):
        self.error_callback = None
        self.name = name
        self.oriented_lattice = None

    def connect_error_message(self, callback):
        """Set the callback function for error messages"""
        self.error_callback = callback

    def get_lattice_ub(self):
        """return oriented lattice object from mtd"""
        if self.name:
            if mtd.doesExist(self.name):
                return mtd[self.name].getExperimentInfo(0).sample().getOrientedLattice()
            err_msg = f"Workspace {self.name} does not exist\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return False
        return False

    def get_ub_matrix_from_lattice(self, params):
        """check and return ub matrix using lattice parameters"""
        # u and v cannot be colinear ; see projections crossproduct of u and v
        ub_matrix = []
        if not self.validate_lattice(params):
            err_msg = "uv and vx arrays need to be non co-linear\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return ub_matrix
        try:
            uvec = numpy.array([params["latt_ux"], params["latt_uy"], params["latt_uz"]])
            vvec = numpy.array([params["latt_vx"], params["latt_vy"], params["latt_vz"]])
            oriented_lattice = OrientedLattice(
                params["latt_a"],
                params["latt_b"],
                params["latt_c"],
                params["latt_alpha"],
                params["latt_beta"],
                params["latt_gamma"],
            )
            oriented_lattice.setUFromVectors(uvec, vvec)
            ub_matrix = oriented_lattice.getUB()
            self.oriented_lattice = oriented_lattice
            return ub_matrix
        except ValueError as value_error:
            err_msg = f"Invalid lattices: {value_error}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return ub_matrix

    def get_lattice_from_ub_matrix(self, ub_matrix):
        """check and return lattice parameters using ub matrix"""
        ub_matrix = numpy.array(ub_matrix)
        if self.validate_matrix(ub_matrix):
            oriented_lattice = OrientedLattice()
            oriented_lattice.setUB(ub_matrix)
            self.oriented_lattice = oriented_lattice
            return oriented_lattice
        err_msg = "Invalid values in matrix\n"
        logger.error(err_msg)
        if self.error_callback:
            self.error_callback(err_msg)
        return None

    def validate_matrix(self, ub_matrix):
        """validate the ub matrix values"""
        ub_matrix = numpy.array(ub_matrix) if not isinstance(ub_matrix, numpy.ndarray) else ub_matrix
        return ValidateUB(ub_matrix)

    def validate_lattice(self, params):
        """validate the lattice values"""
        uvec = numpy.array([params["latt_ux"], params["latt_uy"], params["latt_uz"]])
        vvec = numpy.array([params["latt_vx"], params["latt_vy"], params["latt_vz"]])
        if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
            return False
        return True

    def set_ub(self, params):
        """Mantid SetUB with current workspace"""
        if self.name:
            workspace = mtd[self.name]
            # some check
            uvec = numpy.array([float(params["latt_ux"]), float(params["latt_uy"]), float(params["latt_uz"])])
            vvec = numpy.array([float(params["latt_vx"]), float(params["latt_vy"]), float(params["latt_vz"])])
            if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
                err_msg = "Invalid values in u and v\n"
                logger.error(err_msg)
                if self.error_callback:
                    self.error_callback(err_msg)
            else:
                try:
                    SetUB(
                        Workspace=workspace,
                        a=float(params["latt_a"]),
                        b=float(params["latt_b"]),
                        c=float(params["latt_c"]),
                        alpha=float(params["alpha"]),
                        beta=float(params["beta"]),
                        gamma=float(params["gamma"]),
                        u=uvec,
                        v=vvec,
                    )
                    logger.information(f"SetUB completed for {self.name}")
                    return True
                except ValueError as value_error:
                    err_msg = f"Invalid lattices: {value_error}\n"
                    logger.error(err_msg)
                    if self.error_callback:
                        self.error_callback(err_msg)
            return False
        return True

    def load_nexus_processed(self, filename):
        """Mantid SetUB with Nexus file"""
        try:
            __processed = LoadNexusProcessed(str(filename))
            oriented_lattice = __processed.sample().getOrientedLattice()
            self.oriented_lattice = oriented_lattice
            return oriented_lattice
        except (RuntimeError, ValueError, IndexError) as exception:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {exception}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None

    def load_nexus_ub(self, filename):
        """Mantid SetUB with Nexus file"""
        try:
            __temp_ub = LoadNexusUB(str(filename))
            oriented_lattice = OrientedLattice()
            oriented_lattice.setUB(__temp_ub)
            self.oriented_lattice = oriented_lattice
            return oriented_lattice
        except (RuntimeError, ValueError, IndexError) as exception:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {exception}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None

    def load_isaw_ub(self, filename):
        """Mantid LoadIsawUB with Isaw file"""
        try:
            __tempws = CreateSingleValuedWorkspace(0.0)
            LoadIsawUB(__tempws, str(filename))
            oriented_lattice = OrientedLattice(__tempws.sample().getOrientedLattice())
            oriented_lattice.setUB(__tempws.sample().getOrientedLattice().getUB())
            self.oriented_lattice = oriented_lattice
            DeleteWorkspace(__tempws)
            return oriented_lattice
        except (RuntimeError, ValueError, IndexError) as exception:
            err_msg = f"Could not open the Isaw file, or could not find UB matrix: {exception}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None
