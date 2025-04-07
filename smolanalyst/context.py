import os
import copy
import inspect
import functools
import pandas as pd
import matplotlib
import matplotlib.pyplot


class ExecutionContext:
    @classmethod
    def cwd(cls):
        """
        Create an ExecutionContext with the current working directory as the secure directory.

        :return: ExecutionContext object
        """
        return cls(os.getcwd())

    def __init__(self, secure_directory):
        """
        Initialize the secure pandas and matplotlib wrapper.

        :param secure_directory: The directory where file operations are allowed
        """
        self.dir = os.path.abspath(secure_directory)

        # Store original methods for restoration.
        self.df = {
            "to_csv": [pd.DataFrame.to_csv, True, "path_or_buf"],
            "to_json": [pd.DataFrame.to_json, True, "path_or_buf"],
            "to_excel": [pd.DataFrame.to_excel, True, "excel_writer"],
            "to_sql": [pd.DataFrame.to_sql, False, None],
            "to_hdf": [pd.DataFrame.to_hdf, False, None],
            "to_orc": [pd.DataFrame.to_orc, False, None],
            "to_pickle": [pd.DataFrame.to_pickle, False, None],
            "to_feather": [pd.DataFrame.to_feather, False, None],
            "to_parquet": [pd.DataFrame.to_parquet, False, None],
            "to_stata": [pd.DataFrame.to_stata, False, None],
            "to_clipboard": [pd.DataFrame.to_clipboard, False, None],
        }

        self.series = {
            "to_csv": [pd.Series.to_csv, True, "path_or_buf"],
            "to_json": [pd.Series.to_json, True, "path_or_buf"],
            "to_excel": [pd.Series.to_excel, True, "excel_writer"],
            "to_pickle": [pd.Series.to_pickle, False, None],
        }

        self.matplotlib = {
            "savefig": [matplotlib.pyplot.savefig, True, ""],
        }

    def _secure_path(self, filepath):
        """
        Ensure that the filepath is within the secure directory and is not the path of an existing file.

        :param filepath: Path to be checked
        :return: Absolute path if valid
        :raises ValueError: If path is outside the secure directory and is not an existing file
        """
        # Handle None or non-string inputs.
        if not filepath or not isinstance(filepath, str):
            raise ValueError(f"File writting failed. Invalid path: {filepath}")

        abs_path = os.path.abspath(filepath)

        # Ensure the path is within the secure directory.
        if not abs_path.startswith(self.dir):
            raise ValueError(f"File writting not allowed outside {self.dir}")

        # Ensure this is not the path  of an existing file.
        if os.path.exists(abs_path):
            raise ValueError(
                f"File {abs_path} already exists. Overwriting is not allowed."
            )

        return abs_path

    def _secure_write_method(self, write_method, arg_name):
        """
        Right now just prevent file writing.

        :param original_method: The original method to secure
        :return: A secured version of the method
        """

        @functools.wraps(write_method)
        def secure_method(*args, **kwargs):
            if arg_name == "":
                args_list = list(args)
                args_list[0] = self._secure_path(args_list[0])
                return write_method(*args_list, **kwargs)
            else:
                sig = inspect.signature(write_method)
                bound_arguments = sig.bind(*args, **kwargs)
                bound_arguments.apply_defaults()
                filepath = bound_arguments.arguments.get(arg_name)
                bound_arguments.arguments[arg_name] = self._secure_path(filepath)
                return write_method(*bound_arguments.args, **bound_arguments.kwargs)

        return secure_method

    def _unallowed_write_method(self, write_method):
        @functools.wraps(write_method)
        def unallowed_method(*args, **kwargs):
            raise ValueError(
                f"File writing method {write_method.__name__} not allowed."
            )

        return unallowed_method

    def patch(self, module, name, values):
        [method, allowed, arg_name] = values
        new_method = (
            self._secure_write_method(method, arg_name)
            if allowed
            else self._unallowed_write_method(method)
        )
        setattr(module, name, new_method)

    def __enter__(self):
        # Monkey patch pandas dataframe methods.
        for name, values in self.df.items():
            self.patch(pd.DataFrame, name, values)

        # Monkey patch pandas series methods.
        for name, values in self.series.items():
            self.patch(pd.Series, name, values)

        # Monkey patch matplotlib methods.
        for name, values in self.matplotlib.items():
            self.patch(matplotlib.pyplot, name, values)

        # Store original matplotlib rcParams for restoration.
        self.original_rcparams = copy.deepcopy(matplotlib.rcParams)

        # Set matplotlib to headless mode.
        matplotlib.rcParams["backend"] = "Agg"

    def __exit__(self, type, value, traceback):
        # Restore original methods.
        for name, values in self.df.items():
            setattr(pd.DataFrame, name, values[0])

        for name, values in self.series.items():
            setattr(pd.Series, name, values[0])

        for name, values in self.matplotlib.items():
            setattr(matplotlib.pyplot, name, values[0])

        # Restore original matplotlib settings.
        matplotlib.rcParams.update(self.original_rcparams)
