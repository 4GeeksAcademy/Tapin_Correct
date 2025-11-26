"""
Gamification Module for Tapin

Handles achievements, badges, and volunteer progression.
"""

from flask import Blueprint

# Expose the blueprint defined in achievement_checker.py
from .achievement_checker import gamification_api as gamification_blueprint

__all__ = ["gamification_blueprint"]
