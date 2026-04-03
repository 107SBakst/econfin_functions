"""
econfin_functions - A Python package for economic and financial data functions

This package provides functions to access and process economic and financial data
from various sources, starting with Israel's Central Bureau of Statistics (CBS) API.
"""

__version__ = "0.2.0"
__author__ = "Samuel Bakst"
__email__ = "107sbakst@gmail.com"

from .israel_cbs import il_cbs_api

__all__ = ["il_cbs_api"]