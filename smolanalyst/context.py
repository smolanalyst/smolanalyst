import os
import contextlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import copy
import functools


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
        self.original_methods = {
            "dataframe": {
                "to_json": pd.DataFrame.to_json,
                "to_csv": pd.DataFrame.to_csv,
                "to_excel": pd.DataFrame.to_excel,
                "to_sql": pd.DataFrame.to_sql,
                "to_hdf": pd.DataFrame.to_hdf,
                "to_orc": pd.DataFrame.to_orc,
                "to_pickle": pd.DataFrame.to_pickle,
                "to_feather": pd.DataFrame.to_feather,
                "to_parquet": pd.DataFrame.to_parquet,
                "to_stata": pd.DataFrame.to_stata,
                "to_clipboard": pd.DataFrame.to_clipboard,
            },
            "series": {
                "to_csv": pd.Series.to_csv,
                "to_pickle": pd.Series.to_pickle,
                "to_json": pd.Series.to_json,
                "to_excel": pd.Series.to_excel,
            },
            "matplotlib": {
                "savefig": plt.savefig,
            },
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
            return filepath

        abs_path = os.path.abspath(filepath)

        # Ensure the path is within the secure directory.
        if not abs_path.startswith(self.dir):
            raise ValueError(f"File writting not allowed outside {self.dir}")

        # Ensure this is not the pathof an existing file.
        if os.path.exists(abs_path):
            raise ValueError(
                f"File {abs_path} already exists. Overwriting is not allowed."
            )

        return abs_path

    def _secure_write_method(self, write_method):
        """
        Right now just prevent file writing.

        :param original_method: The original method to secure
        :return: A secured version of the method
        """

        @functools.wraps(write_method)
        def secure_method(*args, **kwargs):
            raise ValueError("File writing is not allowed")

        return secure_method

    def _secure_dataframe_write_method(self, dataframe_write_method):
        return self._secure_write_method(dataframe_write_method)

    def _secure_series_write_method(self, series_write_method):
        return self._secure_write_method(series_write_method)

    def _secure_matplotlib_write_method(self, matplotlib_write_method):
        return self._secure_write_method(matplotlib_write_method)

    @contextlib.contextmanager
    def secure_context(self):
        """
        Context manager to apply and then revert security patches.

        Usage:
        with secure_context():
            # Your code here
        """
        try:
            # Store original matplotlib rcParams for restoration.
            self.original_rcparams = copy.deepcopy(matplotlib.rcParams)

            # Monkey patch allowed modules.
            for name, method in self.original_methods["dataframe"].items():
                setattr(pd.DataFrame, name, self._secure_dataframe_write_method(method))

            for name, method in self.original_methods["series"].items():
                setattr(pd.Series, name, self._secure_series_write_method(method))

            for name, method in self.original_methods["matplotlib"].items():
                setattr(matplotlib, name, self._secure_matplotlib_write_method(method))

            yield
        finally:
            # Restore original matplotlib settings.
            matplotlib.rcParams.update(self.original_rcparams)

            # Restore original methods.
            for name in self.original_methods["dataframe"].keys():
                setattr(pd.DataFrame, name, self.original_methods["dataframe"][name])

            for name in self.original_methods["series"].keys():
                setattr(pd.Series, name, self.original_methods["series"][name])

            for name in self.original_methods["matplotlib"].keys():
                setattr(matplotlib, name, self.original_methods["matplotlib"][name])
