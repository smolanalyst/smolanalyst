#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmolAnalyst Constants - Central location for application constants.
"""

# Application constants
APP_NAME = "smolanalyst"
ENV_NAME = "smolanalyst"
ENV_VERSION = "0.1.1"

# Container directories
WORK_DIR = "/smolanalyst"
SOURCE_FILES_DIR = "/source_files"

# Allowed imports for the agent's execution environment
ADDITIONAL_AUTHORIZED_IMPORTS = [
    "os",
    "posixpath",
    "numpy",
    "pandas",
    "matplotlib",
    "matplotlib.pyplot",
]
