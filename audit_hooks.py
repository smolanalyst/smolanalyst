import os
import tempfile
from pathlib import Path

# File operation events to monitor.
file_operations = {
    "open",  # Built-in open function.
    "os.open",  # Low-level file open.
}

# File modification operations that should always be blocked.
file_modification_operations = {
    "os.replace",  # File replacement.
    "os.unlink",  # File deletion.
    "os.rename",  # File renaming.
    "os.mkdir",  # Directory creation.
    "os.makedirs",  # Recursive directory creation.
    "os.rmdir",  # Remove directory.
    "os.removedirs",  # Remove directories recursively.
    "os.truncate",  # Truncate file.
    "os.symlink",  # Create symbolic link.
    "os.link",  # Create hard link.
    "os.chmod",  # Change permissions.
    "os.chown",  # Change ownership.
    # "os.remove",  # File removal (alias for unlink) - apparently required for tempfile.
}


# Is the given file within the tempdir.
def is_file_in_tmp(file):
    abs_tmp = tempfile.gettempdir()
    abs_file = os.path.abspath(file)
    common_prefix = os.path.commonpath([abs_tmp, abs_file])
    return common_prefix == abs_tmp


# Is the given file within the current working directory.
def is_file_in_cwd(file):
    abs_cwd = os.path.abspath(os.getcwd())
    abs_file = os.path.abspath(file)
    common_prefix = os.path.commonpath([abs_cwd, abs_file])
    return common_prefix == abs_cwd


# Raise exception if the given file is not in tempdir, not in cwd or is an existing file.
def validate_file_is_writable(file):
    if is_file_in_tmp(file):
        return

    if not is_file_in_cwd(file):
        raise PermissionError(
            f"Write operation is not permitted outside of cwd ('{file}')."
        )

    if Path(file).exists():
        raise FileExistsError(f"Can't overwrite existing file ('{file}').")


def write_audit_hook(event, args):
    # First, handle operations that should always be blocked.
    if event in file_modification_operations:
        file = args[0] if args else "."
        raise PermissionError(
            f"File modification operation '{event}' on '{file}' is not permitted."
        )

    # Then handle write operations.
    elif event in file_operations:
        # Handle write using open.
        if event == "open" and len(args) >= 1:
            file = args[0]
            mode = args[1] if len(args) >= 2 else "r"

            if isinstance(mode, str) and ("w" in mode or "a" in mode or "+" in mode):
                validate_file_is_writable(file)

        # Handle write using os.open calls.
        elif event == "os.open" and len(args) >= 1:
            file = args[0]
            flags = args[1] if len(args) >= 2 else 0

            write_flags = {os.O_WRONLY, os.O_RDWR, os.O_CREAT, os.O_TRUNC, os.O_APPEND}
            if any(flags & flag for flag in write_flags):
                validate_file_is_writable(file)
