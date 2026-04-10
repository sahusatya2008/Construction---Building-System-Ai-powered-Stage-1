"""
Soil Analysis Engine Module
===========================
Comprehensive soil analysis for foundation design.

Implements:
- Soil bearing capacity calculations
- Foundation type recommendations
- Settlement estimation
- Soil classification analysis

Based on civil engineering principles and geotechnical standards.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np


class SoilType(str, Enum):
    """
    Soil type classification based on grain size and properties.
    
    Each soil type has characteristic properties affecting
    foundation design and structural stability.
    """
    CLAY = "clay"
    SAND = "sand"
    GRAVEL = "gravel"
    SILT = "silt"
    ROCKY = "rocky"
    LOAM = "loam"
    PEAT = "peat"
    MIXED = "mixed"
    

class FoundationType(str, Enum):
    """
    Foundation types based on load transfer mechanism.
    """
    SHALLOW_ISOLATED = "shallow_isolated"
    SHALLOW_STRIP = "shallow_strip"
    SHALLOW_RAFT = "shallow_raft"
    DEEP_PILE = "deep_pile"
    DEEP_PIER = "deep_pier"
    MAT = "mat"
    COMBINED = "combined"


@dataclass
class SoilProperties:
    """
    Engineering properties of soil.
    
    Attributes:
        soil_type: Classification of soil
        bearing_capacity: Allowable bearing capacity (kN/m²)
        cohesion: Soil cohesion (kN/m²)
        angle_of_friction: Internal friction angle (degrees)
        unit_weight: Unit weight of soil (kN/m³)
        void_ratio: Ratio of void volume to solid volume
        permeability: Hydraulic conductivity (m/s)
        compressibility: Compression index
        settlement_rate: Expected settlement rate (mm/year)
    """
    soil_type: SoilType
    bearing_capacity: float  # kN/m² (kPa)
    cohesion: float  # kN/m²
    angle_of_friction: float  # degrees
    unit_weight: float  # kN/m³
    void_ratio: float
    permeability: float  # m/s
    compressibility: float
    settlement_rate: float  # mm/year
    
    @classmethod
    def get_default_properties(cls, soil_type: SoilType) -> "SoilProperties":
        """
        Get default engineering properties for a soil type.
        
        Values are based on typical geotechnical engineering references.
        
        Args:
            soil_type: Type of soil
            
        Returns:
            SoilProperties: Default properties for the soil type
        """
        # Default properties based on soil type
        # Values from geotechnical engineering handbooks
        defaults: Dict[SoilType, Dict] = {
            SoilType.CLAY: {
                "bearing_capacity": 150.0,  # kN/m²
                "cohesion": 25.0,  # kN/m²
                "angle_of_friction": 5.0,  # degrees
                "unit_weight": 18.0,  # kN/m³
                "void_ratio": 0.8,
                "permeability": 1e-9,  # m/s
                "compressibility": 0.25,
                "settlement_rate": 25.0,  # mm/year
            },
            SoilType.SAND: {
                "bearing_capacity": 250.0,
                "cohesion": 0.0,
                "angle_of_friction": 32.0,
                "unit_weight": 19.0,
                "void_ratio": 0.6,
                "permeability": 1e-4,
                "compressibility": 0.05,
                "settlement_rate": 5.0,
            },
            SoilType.GRAVEL: {
                "bearing_capacity": 450.0,
                "cohesion": 0.0,
                "angle_of_friction": 38.0,
                "unit_weight": 20.0,
                "void_ratio": 0.4,
                "permeability": 1e-2,
                "compressibility": 0.02,
                "settlement_rate": 2.0,
            },
            SoilType.SILT: {
                "bearing_capacity": 100.0,
                "cohesion": 10.0,
                "angle_of_friction": 28.0,
                "unit_weight": 17.5,
                "void_ratio": 0.7,
                "permeability": 1e-7,
                "compressibility": 0.15,
                "settlement_rate": 15.0,
            },
            SoilType.ROCKY: {
                "bearing_capacity": 1000.0,
                "cohesion": 100.0,
                "angle_of_friction": 45.0,
                "unit_weight": 25.0,
                "void_ratio": 0.1,
                "permeability": 1e-5,
                "compressibility": 0.01,
                "settlement_rate": 1.0,
            },
            SoilType.LOAM: {
                "bearing_capacity": 180.0,
                "cohesion": 15.0,
                "angle_of_friction": 25.0,
                "unit_weight": 18.5,
                "void_ratio": 0.65,
                "permeability": 1e-6,
                "compressibility": 0.12,
                "settlement_rate": 10.0,
            },
            SoilType.PEAT: {
                "bearing_capacity": 30.0,
                "cohesion": 5.0,
                "angle_of_friction": 10.0,
                "unit_weight": 12.0,
                "void_ratio": 2.5,
                "permeability": 1e-6,
                "compressibility": 0.8,
                "settlement_rate": 100.0,
            },
            SoilType.MIXED: {
                "bearing_capacity": 200.0,
                "cohesion": 12.0,
                "angle_of_friction": 28.0,
                "unit_weight": 18.5,
                "void_ratio": 0.6,
                "permeability": 1e-5,
                "compressibility": 0.1,
                "settlement_rate": 12.0,
            },
        }
        
        props = defaults.get(soil_type, defaults[SoilType.MIXED])
        
        return cls(
            soil_type=soil_type,
            bearing_capacity=props["bearing_capacity"],
            cohesion=props["cohesion"],
            angle_of_friction=props["angle_of_friction"],
            unit_weight=props["unit_weight"],
            void_ratio=props["void_ratio"],
            permeability=props["permeability"],
            compressibility=props["compressibility"],
            settlement_rate=props["settlement_rate"],
        )


@dataclass
class FoundationRecommendation:
    """
    Foundation design recommendation.
    
    Attributes:
        foundation_type: Recommended foundation type
        depth: Foundation depth (m)
        width: Foundation width (m)
        allowable_bearing_pressure: Safe bearing pressure (kN/m²)
        settlement_estimate: Expected settlement (mm)
        safety_factor: Factor of safety
        notes: Additional recommendations
    """
    foundation_type: FoundationType
    depth: float  # m
    width: float  # m
    allowable_bearing_pressure: float  # kN/m²
    settlement_estimate: float  # mm
    safety_factor: float
    notes: List[str]


class SoilAnalysisEngine:
    """
    Main soil analysis engine for foundation design.
    
    Provides comprehensive geotechnical analysis including:
    - Bearing capacity calculation
    - Foundation type selection
    - Settlement estimation
    - Safety factor verification
    """
    
    # Constants for bearing capacity factors (Terzaghi's method)
    # Nc, Nq, Nγ factors for general shear failure
    
    @staticmethod
    def calculate_bearing_capacity_factors(
        phi: float,
    ) -> Tuple[float, float, float]:
        """
        Calculate Terzaghi's bearing capacity factors.
        
        Nc: Cohesion factor
        Nq: Surcharge factor
        Nγ: Unit weight factor
        
        Formulas:
        Nq = e^(πtanφ) × tan²(45 + φ/2)
        Nc = (Nq - 1) × cot(φ)
        Nγ = 2 × (Nq + 1) × tan(φ)
        
        Args:
            phi: Angle of internal friction (degrees)
            
        Returns:
            Tuple[float, float, float]: (Nc, Nq, Nγ)
        """
        phi_rad = np.radians(phi)
        
        # Nq factor
        nq = np.exp(np.pi * np.tan(phi_rad)) * (np.tan(np.pi/4 + phi_rad/2)) ** 2
        
        # Nc factor
        if phi > 0:
            nc = (nq - 1) / np.tan(phi_rad)
        else:
            nc = 2 * np.pi + 2  # For φ = 0 (clay)
        
        # Nγ factor
        ngamma = 2 * (nq + 1) * np.tan(phi_rad)
        
        return nc, nq, ngamma
    
    @staticmethod
    def calculate_ultimate_bearing_capacity(
        soil: SoilProperties,
        foundation_width: float,
        foundation_depth: float,
        shape_factors: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate ultimate bearing capacity using Terzaghi's equation.
        
        General Bearing Capacity Equation:
        qu = cNcSc + qNqSq + 0.5γBNγSγ
        
        where:
        - c = soil cohesion
        - Nc, Nq, Nγ = bearing capacity factors
        - q = surcharge (γ × Df)
        - γ = unit weight of soil
        - B = foundation width
        - Sc, Sq, Sγ = shape factors
        
        Args:
            soil: Soil properties
            foundation_width: Foundation width (m)
            foundation_depth: Foundation depth (m)
            shape_factors: Optional shape correction factors
            
        Returns:
            float: Ultimate bearing capacity (kN/m²)
        """
        # Get bearing capacity factors
        nc, nq, ngamma = SoilAnalysisEngine.calculate_bearing_capacity_factors(
            soil.angle_of_friction
        )
        
        # Default shape factors for strip footing
        if shape_factors is None:
            shape_factors = {
                "sc": 1.0,  # Strip footing
                "sq": 1.0,
                "sgamma": 1.0,
            }
        
        # Surcharge from soil above foundation base
        q = soil.unit_weight * foundation_depth
        
        # Ultimate bearing capacity
        qu = (
            soil.cohesion * nc * shape_factors["sc"]
            + q * nq * shape_factors["sq"]
            + 0.5 * soil.unit_weight * foundation_width * ngamma * shape_factors["sgamma"]
        )
        
        return qu
    
    @staticmethod
    def calculate_allowable_bearing_capacity(
        ultimate_capacity: float,
        safety_factor: float = 3.0,
    ) -> float:
        """
        Calculate allowable bearing capacity with safety factor.
        
        Formula: qa = qu / FS
        
        Args:
            ultimate_capacity: Ultimate bearing capacity (kN/m²)
            safety_factor: Factor of safety (typically 2.5-3.0)
            
        Returns:
            float: Allowable bearing capacity (kN/m²)
        """
        return ultimate_capacity / safety_factor
    
    @staticmethod
    def estimate_settlement(
        soil: SoilProperties,
        foundation_width: float,
        foundation_length: float,
        applied_pressure: float,
        foundation_depth: float,
    ) -> float:
        """
        Estimate total settlement of shallow foundation.
        
        Settlement components:
        1. Immediate (elastic) settlement
        2. Consolidation settlement
        
        Immediate Settlement (Schmertmann's method simplified):
        Si = q₀ × B × (1 - ν²) / Es × Iz
        
        Consolidation Settlement:
        Sc = Cc × H × log((σ'v0 + Δσ)/σ'v0) / (1 + e₀)
        
        Args:
            soil: Soil properties
            foundation_width: Foundation width (m)
            foundation_length: Foundation length (m)
            applied_pressure: Net applied pressure (kN/m²)
            foundation_depth: Foundation depth (m)
            
        Returns:
            float: Estimated total settlement (mm)
        """
        # Elastic modulus estimation (simplified)
        # Es ≈ 500 × qu for clay, Es ≈ 1000 × N for sand
        if soil.cohesion > 0:
            # Clay-like soil
            elastic_modulus = 500 * soil.bearing_capacity  # kN/m²
        else:
            # Sand-like soil
            elastic_modulus = 300 * soil.bearing_capacity  # kN/m²
        
        # Poisson's ratio
        nu = 0.3 if soil.cohesion == 0 else 0.4
        
        # Influence factor (simplified)
        iz = 0.6  # Typical value for flexible footing
        
        # Immediate settlement (mm)
        immediate_settlement = (
            applied_pressure
            * foundation_width
            * (1 - nu ** 2)
            / elastic_modulus
            * iz
            * 1000  # Convert to mm
        )
        
        # Consolidation settlement (for cohesive soils)
        if soil.cohesion > 0 and soil.compressibility > 0:
            # Stress increase at foundation level
            sigma_v0 = soil.unit_weight * foundation_depth
            delta_sigma = applied_pressure
            
            # Influence depth (2B for typical cases)
            h = 2 * foundation_width
            
            # Consolidation settlement
            if sigma_v0 > 0:
                consolidation_settlement = (
                    soil.compressibility
                    * h
                    * np.log10((sigma_v0 + delta_sigma) / sigma_v0)
                    * 1000  # Convert to mm
                )
            else:
                consolidation_settlement = 0
        else:
            consolidation_settlement = 0
        
        return immediate_settlement + consolidation_settlement
    
    @staticmethod
    def recommend_foundation_type(
        soil: SoilProperties,
        total_load: float,  # kN
        foundation_area: float,  # m²
        building_height: float,  # m
        number_of_stories: int,
    ) -> FoundationRecommendation:
        """
        Recommend appropriate foundation type based on soil and load conditions.
        
        Decision criteria:
        1. Bearing capacity vs required pressure
        2. Settlement characteristics
        3. Building type and height
        4. Soil type and properties
        
        Args:
            soil: Soil properties
            total_load: Total structural load (kN)
            foundation_area: Available foundation area (m²)
            building_height: Building height (m)
            number_of_stories: Number of stories
            
        Returns:
            FoundationRecommendation: Foundation design recommendation
        """
        notes: List[str] = []
        
        # Required bearing pressure
        required_pressure = total_load / foundation_area
        
        # Determine foundation depth (frost depth consideration)
        min_depth = max(0.6, building_height / 15)  # Simplified rule
        
        # Check if shallow foundation is feasible
        if required_pressure <= soil.bearing_capacity * 0.5:
            # Low pressure, shallow foundation suitable
            if soil.bearing_capacity >= 300:
                # Good soil, isolated footings
                foundation_type = FoundationType.SHALLOW_ISOLATED
                depth = min_depth
                width = np.sqrt(total_load / (soil.bearing_capacity * 0.5))
                notes.append("Isolated footings suitable for good soil conditions")
            else:
                # Marginal soil, strip footings
                foundation_type = FoundationType.SHALLOW_STRIP
                depth = min_depth + 0.3
                width = total_load / (soil.bearing_capacity * 0.5 * 10)  # Assume 10m length
                notes.append("Strip footings recommended for load distribution")
        
        elif required_pressure <= soil.bearing_capacity * 0.8:
            # Moderate pressure, may need raft
            if number_of_stories > 3 or building_height > 12:
                foundation_type = FoundationType.SHALLOW_RAFT
                depth = min_depth + 0.5
                width = np.sqrt(foundation_area)
                notes.append("Raft foundation for multi-story building")
            else:
                foundation_type = FoundationType.SHALLOW_STRIP
                depth = min_depth + 0.3
                width = total_load / (soil.bearing_capacity * 0.7 * 10)
                notes.append("Reinforced strip footings recommended")
        
        else:
            # High pressure or poor soil, deep foundation needed
            if soil.soil_type == SoilType.PEAT or soil.bearing_capacity < 100:
                foundation_type = FoundationType.DEEP_PILE
                depth = 10.0  # Typical pile depth
                width = 0.4  # Typical pile diameter
                notes.append("Pile foundation required for very poor soil")
                notes.append("End bearing on competent stratum required")
            elif soil.soil_type == SoilType.CLAY:
                foundation_type = FoundationType.DEEP_PIER
                depth = 8.0
                width = 0.6
                notes.append("Drilled pier foundation for clay soil")
            else:
                foundation_type = FoundationType.MAT
                depth = min_depth + 1.0
                width = np.sqrt(foundation_area)
                notes.append("Mat foundation for high loads")
        
        # Calculate actual bearing capacity
        ultimate_capacity = SoilAnalysisEngine.calculate_ultimate_bearing_capacity(
            soil, width, depth
        )
        allowable_capacity = SoilAnalysisEngine.calculate_allowable_bearing_capacity(
            ultimate_capacity
        )
        
        # Estimate settlement
        settlement = SoilAnalysisEngine.estimate_settlement(
            soil, width, width, required_pressure, depth
        )
        
        # Calculate safety factor
        safety_factor = ultimate_capacity / required_pressure if required_pressure > 0 else 3.0
        
        # Add settlement-based notes
        if settlement > 25:
            notes.append(f"Warning: Estimated settlement ({settlement:.1f}mm) may be excessive")
        elif settlement > 10:
            notes.append(f"Moderate settlement expected ({settlement:.1f}mm)")
        else:
            notes.append(f"Settlement within acceptable limits ({settlement:.1f}mm)")
        
        return FoundationRecommendation(
            foundation_type=foundation_type,
            depth=round(depth, 2),
            width=round(width, 2),
            allowable_bearing_pressure=round(min(allowable_capacity, soil.bearing_capacity), 1),
            settlement_estimate=round(settlement, 1),
            safety_factor=round(safety_factor, 2),
            notes=notes,
        )
    
    @staticmethod
    def analyze_soil_compatibility(
        soil: SoilProperties,
        required_bearing_capacity: float,
        max_settlement: float = 25.0,  # mm
    ) -> Tuple[bool, List[str], float]:
        """
        Analyze soil compatibility with structural requirements.
        
        Args:
            soil: Soil properties
            required_bearing_capacity: Required bearing capacity (kN/m²)
            max_settlement: Maximum allowable settlement (mm)
            
        Returns:
            Tuple containing:
            - bool: Is compatible
            - List[str]: Issues/warnings
            - float: Compatibility score (0-1)
        """
        issues: List[str] = []
        score = 1.0
        
        # Check bearing capacity
        if soil.bearing_capacity < required_bearing_capacity:
            issues.append(
                f"Bearing capacity ({soil.bearing_capacity} kN/m²) "
                f"below required ({required_bearing_capacity} kN/m²)"
            )
            score *= 0.3
        elif soil.bearing_capacity < required_bearing_capacity * 1.5:
            issues.append("Bearing capacity marginal - consider foundation optimization")
            score *= 0.8
        
        # Check settlement characteristics
        if soil.settlement_rate > max_settlement:
            issues.append(
                f"High settlement rate ({soil.settlement_rate} mm/year) "
                f"may exceed limits"
            )
            score *= 0.5
        
        # Check soil type specific issues
        if soil.soil_type == SoilType.PEAT:
            issues.append("Peat soil highly unsuitable for construction")
            score *= 0.1
        elif soil.soil_type == SoilType.CLAY:
            if soil.compressibility > 0.3:
                issues.append("Highly compressible clay - expect significant settlement")
                score *= 0.6
        elif soil.soil_type == SoilType.SILT:
            issues.append("Silt may liquefy under seismic loading")
            score *= 0.7
        
        # Check drainage
        if soil.permeability < 1e-8:
            issues.append("Poor drainage - consider dewatering during construction")
            score *= 0.85
        
        is_compatible = len(issues) == 0 or score > 0.3
        
        return is_compatible, issues, round(score, 2)