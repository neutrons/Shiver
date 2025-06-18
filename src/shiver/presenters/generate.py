"""Presenter for the Generate tab"""

import json

CONFIG_TEMPLATE = """#!/usr/bin/env python


def define_data_set(**kwargs) -> list:  # pylint: disable=unused-argument
    '''Singleton wrapper for generate configuration.'''
    data_set_list = []
    data_set = DATA_SET_TO_BE_REPLACED
    data_set_list.append(data_set)
    return data_set_list

if __name__ == "__main__":
    print("This is a module for generate configuration.")
"""


class GeneratePresenter:
    """Generate Presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        # connect generate callback
        self.view.connect_generate_mde_callback(self.do_generate_mde)

        # connect save configuration callback
        self.view.connect_save_configuration_callback(self.do_save_configuration)

        # connect error callback
        self.model.connect_error_message(view.show_error_message)

        # connect finish callback
        # NOTE: since the backend algorithm was exactly written for asynchronous
        #       running but executed as such regardless, we need to perform some
        #       atomic lock for the UI element to prevent racing condition induced
        #       error from the Mantid side.
        self.model.connect_generate_mde_finish_callback(view.generate_mde_finish_callback)
        # connect with advanced options changes
        self.view.reduction_parameters.connect_advanced_apply_callback(self.advanced_dialog_update)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def do_generate_mde(self):
        """Slot for Generate button.

        Notes
        -----
        This function will collection configuration information from the view
        and pass it to the model.
        """
        config_dict = self.get_config_dict_from_view()

        if not config_dict:
            return

        self.model.generate_mde(config_dict)

    def do_save_configuration(self):
        """Slot for Save Configuration button.

        Notes
        -----
        This function will collect configuration information from the view and
        save it to a python file similar to define_dataset.py.
        """
        config_dict = self.get_config_dict_from_view()

        if not config_dict:
            return

        # Ask user to specify a filename and output directory
        filepath = self.view.get_save_configuration_filepath(
            default_filename=config_dict["mde_name"],
            default_output_dir=config_dict["output_dir"],
        )

        # in case user cancels the dialog
        if not filepath:
            return

        if not filepath.endswith(".py"):
            filepath += ".py"

        # use json to dump config_dict to string
        config_dict_str = json.dumps(config_dict, indent=4)
        config_dict_str = config_dict_str.replace("null", "None")
        config_dict_str = config_dict_str.replace("true", "True")
        config_dict_str = config_dict_str.replace("false", "False")
        config_dict_str = config_dict_str[:-1] + "\t}"

        content = CONFIG_TEMPLATE.replace("DATA_SET_TO_BE_REPLACED", config_dict_str)

        with open(filepath, "w", encoding="UTF-8") as config_file:
            config_file.write(content)

    def get_config_dict_from_view(self) -> dict:
        """Get configuration dictionary from generate view."""
        config_dict = self.view.as_dict()

        if not config_dict:
            return {}

        # translate filelist to string
        config_dict["filename"] = translate_filelist_to_string(config_dict.get("filename", []))

        # remove all None pairs
        config_dict = {k: v for k, v in config_dict.items() if v is not None}

        advanced_options = config_dict.get("AdvancedOptions", {})
        if advanced_options:
            config_dict["AdvancedOptions"] = {k: v for k, v in advanced_options.items() if v is not None}

        sample_parameters = config_dict.get("SampleParameters", {})
        if sample_parameters:
            config_dict["SampleParameters"] = {k: v for k, v in sample_parameters.items() if v is not None}

        polarized_options = config_dict.get("PolarizedOptions", {})
        if polarized_options:
            config_dict["PolarizedOptions"] = {k: v for k, v in polarized_options.items() if v is not None}

        return config_dict

    def advanced_dialog_update(self, advanced_options):
        """update the oncat with goniometer data"""
        self.view.update_raw_data_widget_selection(update_angle_pv=True, angle_pv=advanced_options["Goniometer"])


def translate_filelist_to_string(filelist: list) -> str:
    """Translate filelist to string.

    Parameters
    ----------
    filelist : list
        List of files

    Returns
    -------
    str
        Comma-separated string of files.

    Notes
    -----
    Mantid's MultipleFileProperty is expecting a string representation of
    nested lists, e.g.

    For a single layer list, the conversion is simple:

    >>> filelist = ['/tmp/file1', '/tmp/file2']
    to
    >>> filelist = "/tmp/file1, /tmp/file2"

    For a nested list, the conversion is slightly more complicated:
    >>> filelist = [['/tmp/file1', '/tmp/file2'], ['/tmp/file3']]
    to
    >>> filelist = "/tmp/file1+/tmp/file2, /tmp/file3"
    """
    if not filelist:
        return ""

    for index, item in enumerate(filelist):
        if isinstance(item, list):
            filelist[index] = "+".join(item)
    return ", ".join(filelist)
