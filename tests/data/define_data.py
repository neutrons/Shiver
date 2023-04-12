#!/usr/bin/env python
"""Define data demo for test."""
import os


def define_data_set(**kwargs) -> list:
    """Function serve as singleton for data set definition."""
    mde_folder = os.path.join(os.path.dirname(__file__), "mde")
    raw_data_folder = os.path.join(os.path.dirname(__file__), "raw")
    normalization_data_folder = os.path.join(os.path.dirname(__file__), "normalization")

    data_set_list = []
    # data set 1
    # NOTE: using existing data for unit testing
    data_set = {
        "Runs": range(
            178921, 178927
        ),  # List of runs, or list of lists of runs that are added together
        "BackgroundRuns": None,  # range(297325,297337)Options: None;list of runs that are added together
        "RawDataFolder": raw_data_folder,  # Options:raw_data_folder string
        "RawDataFolderBackground": None,  # Options:None (same as the raw data); bknd_raw_data_folder string
        "BackgroundScaling": 1,  # Options: None (same as 1); scaling factor
        "MdeFolder": mde_folder,  # Options:mde_folder string
        "MdeName": "merged_mde_MnO_25meV_5K_unpol_178921-178926",  # Options:mde_name string
        "BackgroundMdeName": None,  # Options:None;bg_mde_name string
        "MaskingDataFile": None,  # Options:None;data_file_name
        "NormalizationDataFile": os.path.join(
            normalization_data_folder, "TiZr.nxs"
        ),  # Options:None;data_file_name
        "SampleLogVariables": {
            "OmegaMotorName": None,
            "Temperature": 3.0,
            "MagneticField": 0.0,
        },  # Options:None;LogVariableName;number
        "USSetup": {
            "a": 5.12484,
            "b": 5.33161,
            "c": 7.31103,
            "alpha": 90,
            "beta": 90,
            "gamma": 90,
            "u": "-0.0493617,4.27279,-4.37293",
            "v": "-0.0706905,-3.18894,-5.85775",
        },
        # Data reduction options
        "Ei": None,  # Options: None;Ei_somehow_determined
        "T0": None,  # Options: None;T0_determined_from_mantid
        "BadPulsesThreshold": None,  # Options: None;bg_pulses_threshold value
        "TimeIndepBackgroundWindow": "Default",  # Options: None;'Default';[Tib_min,Tib_max]
        "E_min": None,  # Options: None;Emin if None the value is -0.95*Ei
        "E_max": None,  # Options: None;Emax if None the value is 0.95*Ei
        "AdditionalDimensions": None,  # Options: None;list of triplets ("name", min, max)
        # Polarized data options
        "PolarizationState": None,  # Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
        "FlippingRatio": None,  # Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
        "PolarizingSupermirrorDeflectionAdjustment": None,  # Options:None;deflection_angle
        "EfCorrectionFunction": None,  # Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
    }

    data_set_list.append(data_set)

    return data_set_list


if __name__ == "__main__":
    print("This is a module for data set definition.")
