#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmolAnalyst Filesystem - File management utilities for SmolAnalyst.

This module provides functions for managing files, including setting permissions
and copying files between directories with appropriate permission handling.
"""

import os
import shutil
import datetime
from pathlib import Path
from typing import Optional


def set_full_permissions(directory: str) -> None:
    set_permissions_recursively(directory, mode=0o777)


def set_permissions_recursively(directory: str, mode: int) -> None:
    """
    Set permissions recursively on all files and directories within the specified directory.

    Args:
        directory (str): Path to the directory to modify permissions.
        mode (int): Permission mode to set.

    Raises:
        ValueError: If the directory doesn't exist.
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")

    try:
        # Walk through all files and directories
        for path in dir_path.glob("**/*"):
            os.chmod(path, mode)

        # Also set permissions on the root directory
        os.chmod(dir_path, mode)
    except Exception as e:
        print(f"Warning: Failed to set permissions on {directory}: {e}")


def copy_from_source(
    source_dir: str,
    target_dir: Optional[str] = None,
    file_mode: int = 0o644,
    dir_mode: int = 0o755,
) -> None:
    """
    Copy all files from the source directory to the target directory (defaults to current
    working directory), preserving the directory structure. Avoids overwriting existing
    files by appending a timestamp to the filename. Sets appropriate permissions on copied files.

    Args:
        source_dir (str): Path to the source directory.
        target_dir (Optional[str]): Path to the target directory. If None, uses current working directory.
        file_mode (int): Permission mode to set on copied files (default: 0o644 - rw-r--r--).
        dir_mode (int): Permission mode to set on created directories (default: 0o755 - rwxr-xr-x).

    Raises:
        ValueError: If the source directory doesn't exist.
    """
    source_path = Path(source_dir)

    if not source_path.exists():
        raise ValueError(f"Source directory does not exist: {source_dir}")

    # Use current working directory if target_dir is not specified
    target_path = Path(target_dir) if target_dir else Path.cwd()

    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    os.chmod(target_path, dir_mode)

    # Walk through all files recursively with pathlib
    for source_file in source_path.glob("**/*"):
        # Skip directories, only process files
        if not source_file.is_file():
            continue

        # Get relative path from source directory
        rel_path = source_file.relative_to(source_path)
        dest_file = target_path / rel_path

        # Create parent directories if needed
        if not dest_file.parent.exists():
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            os.chmod(dest_file.parent, dir_mode)

        # If file exists, append timestamp to the filename
        if dest_file.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = dest_file.with_name(
                f"{dest_file.stem}_{timestamp}{dest_file.suffix}"
            )

        # Copy the file
        shutil.copy2(source_file, dest_file)

        # Set appropriate permissions on the copied file
        os.chmod(dest_file, file_mode)

        print(f"Created: {dest_file.relative_to(target_path)}")
