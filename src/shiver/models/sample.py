"""Model for the Sample Parameters dialog"""

import numpy
from mantid.api import AlgorithmManager
from mantid.geometry import OrientedLattice
from mantid.kernel import Logger

# pylint: disable=no-name-in-module
from mantid.simpleapi import (
    CreateSingleValuedWorkspace,
    DeleteWorkspace,
    LoadIsawUB,
    LoadMD,
    LoadNexusProcessed,
    SaveIsawUB,
    SetUB,
    mtd,
)
from mantidqtinterfaces.DGSPlanner.LoadNexusUB import LoadNexusUB
from mantidqtinterfaces.DGSPlanner.ValidateOL import ValidateUB

from shiver.models.generate import gather_mde_config_dict, save_mde_config_dict

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
        """return oriented lattice object from mtd - if no name provided initialize lattice"""
        if self.name:
            try:
                if mtd.doesExist(self.name):
                    self.oriented_lattice = mtd[self.name].getExperimentInfo(0).sample().getOrientedLattice()
                    return self.oriented_lattice
                err_msg = f"Workspace {self.name} does not exist. Lattice from default parameters\n"
                logger.error(err_msg)
            except RuntimeError:
                err_msg = (
                    f"Workspace {self.name} does not contain an OrientedLattice. Lattice from default parameters\n"
                )
                logger.error(err_msg)
        # no valid name-workspace provided, create lattice with initial params
        params = {
            "a": 1.00000,
            "b": 1.00000,
            "c": 1.00000,
            "alpha": 90.00000,
            "beta": 90.00000,
            "gamma": 90.00000,
            "ux": 0.00000,
            "uy": 0.00000,
            "uz": 1.00000,
            "vx": 1.00000,
            "vy": 0.00000,
            "vz": -0.00000,
        }
        _ = self.get_ub_matrix_from_lattice(params)
        return self.oriented_lattice

    def get_ub_matrix_from_lattice(self, params):
        """check and return ub matrix using lattice parameters"""
        # u and v cannot be colinear ; see projections crossproduct of u and v
        ub_matrix = []
        if not self.validate_lattice(params):
            return ub_matrix
        try:
            uvec = numpy.array([params["ux"], params["uy"], params["uz"]])
            vvec = numpy.array([params["vx"], params["vy"], params["vz"]])
            oriented_lattice = OrientedLattice(
                float(params["a"]),
                float(params["b"]),
                float(params["c"]),
                float(params["alpha"]),
                float(params["beta"]),
                float(params["gamma"]),
            )
            oriented_lattice.setUFromVectors(uvec, vvec)
            ub_matrix = oriented_lattice.getUB()
            self.oriented_lattice = oriented_lattice
            return ub_matrix
        except ValueError:
            return ub_matrix

    def get_lattice_from_ub_matrix(self, ub_matrix):
        """check and return lattice parameters using ub matrix"""
        ub_matrix = numpy.array(ub_matrix)
        if self.validate_matrix(ub_matrix):
            oriented_lattice = OrientedLattice()
            oriented_lattice.setUB(ub_matrix)
            self.oriented_lattice = oriented_lattice
            return oriented_lattice
        return None

    def validate_matrix(self, ub_matrix):
        """validate the ub matrix values"""
        ub_matrix = numpy.array(ub_matrix) if not isinstance(ub_matrix, numpy.ndarray) else ub_matrix
        return ValidateUB(ub_matrix)

    def validate_lattice(self, params):
        """validate the lattice values"""
        uvec = numpy.array([params["ux"], params["uy"], params["uz"]])
        vvec = numpy.array([params["vx"], params["vy"], params["vz"]])
        if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
            return False
        return True

    def set_ub(self, params):
        """Mantid SetUB with current workspace"""
        if self.name and mtd.doesExist(self.name):
            workspace = mtd[self.name]
            # some check
            uvec_cord = params["u"].split(",")
            vvec_cord = params["v"].split(",")
            uvec = numpy.array([float(uvec_cord[0]), float(uvec_cord[1]), float(uvec_cord[2])])
            vvec = numpy.array([float(vvec_cord[0]), float(vvec_cord[1]), float(vvec_cord[2])])
            if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
                err_msg = "Invalid values in u and v\n"
                logger.error(err_msg)
                if self.error_callback:
                    self.error_callback(err_msg)
            else:
                try:
                    SetUB(
                        Workspace=workspace,
                        a=float(params["a"]),
                        b=float(params["b"]),
                        c=float(params["c"]),
                        alpha=float(params["alpha"]),
                        beta=float(params["beta"]),
                        gamma=float(params["gamma"]),
                        u=uvec,
                        v=vvec,
                    )
                    logger.information(f"SetUB completed for {self.name}")
                    # get the saved oriented lattice
                    self.oriented_lattice = workspace.getExperimentInfo(0).sample().getOrientedLattice()
                    # update the mdeconfig
                    update_sample_mde_config(self.name, self.oriented_lattice)
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
        filename_str = str(filename)
        try:
            if self.is_nexus_processed(filename_str):
                __processed = LoadNexusProcessed(filename_str)
                self.oriented_lattice = __processed.sample().getOrientedLattice()
            else:
                __processed = LoadMD(filename_str, MetadataOnly=True)
                self.oriented_lattice = __processed.getExperimentInfo(0).sample().getOrientedLattice()

            return self.oriented_lattice
        except (RuntimeError, ValueError, IndexError) as exception:
            err_msg = f"Could not open the Nexus file, or could not find UB matrix: {exception}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)
            return None

    def is_nexus_processed(self, filename):
        """Return true if the file is NexusProcessed
        - can be loaded through LoadNexusProcessed, else false"""

        alg = AlgorithmManager.create("Load")
        alg.initialize()
        alg.setProperty("Filename", filename)
        return alg.getProperty("LoaderName").value == "LoadNexusProcessed"

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

    def save_isaw(self, filename):
        """Save in Isaw file"""
        try:
            __tempws = CreateSingleValuedWorkspace()
            SetUB(
                Workspace=__tempws,
                a=self.oriented_lattice.a(),
                b=self.oriented_lattice.b(),
                c=self.oriented_lattice.c(),
                alpha=self.oriented_lattice.alpha(),
                beta=self.oriented_lattice.beta(),
                gamma=self.oriented_lattice.gamma(),
                u=self.oriented_lattice.getuVector(),
                v=self.oriented_lattice.getvVector(),
            )
            SaveIsawUB(__tempws, filename)
            DeleteWorkspace(__tempws)

        except (RuntimeError, ValueError) as exception:
            err_msg = f"Could not create the Isaw file: {exception}\n"
            logger.error(err_msg)
            if self.error_callback:
                self.error_callback(err_msg)


def update_sample_mde_config(name, oriented_lattice):
    """Update the MDE Config Sample Parameters, if the MDE Config exists"""

    # updated mde config if it exists
    saved_mde_config = {}
    saved_mde_config.update(gather_mde_config_dict(name))

    # if MDEConfig exists
    if len(saved_mde_config.keys()) != 0:
        # update the MDEConfig with the current value
        sample_data = {}
        sample_data["a"] = oriented_lattice.a()
        sample_data["b"] = oriented_lattice.b()
        sample_data["c"] = oriented_lattice.c()
        sample_data["alpha"] = oriented_lattice.alpha()
        sample_data["beta"] = oriented_lattice.beta()
        sample_data["gamma"] = oriented_lattice.gamma()
        sample_data["u"] = ",".join(str(item) for item in oriented_lattice.getuVector())
        sample_data["v"] = ",".join(str(item) for item in oriented_lattice.getvVector())
        saved_mde_config["SampleParameters"] = sample_data
        save_mde_config_dict(name, saved_mde_config)
