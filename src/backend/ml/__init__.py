"""
Machine Learning Module for Tapin

Handles taste profile generation and personalization.
"""

from flask import Blueprint

# The concrete blueprint is defined in `taste_profile_generator.py` as `ml_api`.
# Import it and expose as `ml_blueprint` for simple registration.
from .taste_profile_generator import ml_api as ml_blueprint

__all__ = ["ml_blueprint"]
