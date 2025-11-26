"""
Admin Module for Tapin

Handles organization verification and platform management.
"""

from flask import Blueprint

# The concrete blueprint lives in `verification.py` (we expose it here as
# `admin_blueprint` so app registration is consistent with integration docs).
from .verification import admin_api as admin_blueprint

__all__ = ["admin_blueprint"]
