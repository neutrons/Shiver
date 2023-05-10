"""Presenter for the Generate tab"""
import json
from pathlib import Path

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
        model.connect_error_message(view.show_error_message)

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

        # use mde_name as filename (use .py extension)
        # use output_dir as directory
        filename = config_dict.get("mde_name", "generated_mde.py")
        output_dir = config_dict.get("output_dir", ".")
        if not filename.endswith(".py"):
            filename += ".py"
        filepath = Path(output_dir) / filename

        # use json to dump config_dict to string
        config_dict_str = json.dumps(config_dict, indent=4)

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

        return config_dict


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
