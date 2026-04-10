"""
Soil analysis engine for foundation design.
"""
from app.domains.soil.engine import (
    SoilAnalysisEngine,
    SoilProperties,
    SoilType,
    FoundationType,
    FoundationRecommendation,
)

__all__ = [
    "SoilAnalysisEngine",
    "SoilProperties",
    "SoilType",
    "FoundationType",
    "FoundationRecommendation",
]