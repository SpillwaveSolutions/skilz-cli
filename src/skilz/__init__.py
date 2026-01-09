"""Skilz - The universal package manager for AI skills."""

__version__ = "1.7.0"
__author__ = "Spillwave"

from skilz.api_client import (
    SkillCoordinates,
    fetch_skill_coordinates,
    is_marketplace_skill_id,
    parse_skill_id,
)
from skilz.errors import SkillNotFoundError, SkilzError

__all__ = [
    "__version__",
    "SkillNotFoundError",
    "SkilzError",
    "SkillCoordinates",
    "parse_skill_id",
    "is_marketplace_skill_id",
    "fetch_skill_coordinates",
]
