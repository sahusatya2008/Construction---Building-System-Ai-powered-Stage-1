"""
Structural Solver Module
========================
Comprehensive structural analysis and design calculations.

Implements:
- Load calculations (dead, live, wind, seismic)
- Beam bending analysis
- Column design
- Structural safety checks
- Load distribution analysis

Based on structural engineering principles and building codes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np


class LoadType(str, Enum):
    """Types of structural loads."""
    DEAD = "dead"
    LIVE = "live"
    WIND = "wind"
    SEISMIC = "seismic"
    SNOW = "snow"
    COMBINED = "combined"


class SupportType(str, Enum):
    """Beam support types."""
    SIMPLY_SUPPORTED = "simply_supported"
    FIXED = "fixed"
    CANTILEVER = "cantilever"
    CONTINUOUS = "continuous"


class MaterialType(str, Enum):
    """Structural material types."""
    CONCRETE = "concrete"
    STEEL = "steel"
    TIMBER = "timber"
    REINFORCED_CONCRETE = "reinforced_concrete"


@dataclass
class MaterialProperties:
    """
    Engineering properties of structural materials.
    
    Attributes:
        material_type: Type of material
        compressive_strength: Characteristic compressive strength (MPa)
        tensile_strength: Characteristic tensile strength (MPa)
        yield_strength: Yield strength for steel (MPa)
        elastic_modulus: Young's modulus (GPa)
        unit_weight: Unit weight (kN/m³)
        poisson_ratio: Poisson's ratio
    """
    material_type: MaterialType
    compressive_strength: float  # MPa
    tensile_strength: float  # MPa
    yield_strength: float  # MPa (for steel)
    elastic_modulus: float  # GPa
    unit_weight: float  # kN/m³
    poisson_ratio: float
    
    @classmethod
    def get_default_properties(cls, material_type: MaterialType) -> "MaterialProperties":
        """Get default properties for a material type."""
        defaults: Dict[MaterialType, Dict] = {
            MaterialType.CONCRETE: {
                "compressive_strength": 25.0,  # MPa (C25)
                "tensile_strength": 2.5,  # MPa
                "yield_strength": 0.0,
                "elastic_modulus": 25.0,  # GPa
                "unit_weight": 24.0,  # kN/m³
                "poisson_ratio": 0.2,
            },
            MaterialType.REINFORCED_CONCRETE: {
                "compressive_strength": 30.0,  # MPa (C30)
                "tensile_strength": 3.0,
                "yield_strength": 415.0,  # Steel reinforcement
                "elastic_modulus": 29.0,
                "unit_weight": 25.0,
                "poisson_ratio": 0.2,
            },
            MaterialType.STEEL: {
                "compressive_strength": 250.0,
                "tensile_strength": 400.0,
                "yield_strength": 250.0,  # Fe250
                "elastic_modulus": 200.0,
                "unit_weight": 78.5,
                "poisson_ratio": 0.3,
            },
            MaterialType.TIMBER: {
                "compressive_strength": 12.0,
                "tensile_strength": 8.0,
                "yield_strength": 0.0,
                "elastic_modulus": 12.0,
                "unit_weight": 6.0,
                "poisson_ratio": 0.35,
            },
        }
        
        props = defaults.get(material_type, defaults[MaterialType.CONCRETE])
        
        return cls(
            material_type=material_type,
            compressive_strength=props["compressive_strength"],
            tensile_strength=props["tensile_strength"],
            yield_strength=props["yield_strength"],
            elastic_modulus=props["elastic_modulus"],
            unit_weight=props["unit_weight"],
            poisson_ratio=props["poisson_ratio"],
        )


@dataclass
class BeamProperties:
    """
    Beam section properties.
    
    Attributes:
        width: Beam width (mm)
        height: Beam height (mm)
        flange_width: Flange width for I-beams (mm)
        flange_thickness: Flange thickness (mm)
        web_thickness: Web thickness (mm)
        area: Cross-sectional area (mm²)
        moment_of_inertia: Second moment of area (mm⁴)
        section_modulus: Section modulus (mm³)
    """
    width: float  # mm
    height: float  # mm
    flange_width: Optional[float] = None
    flange_thickness: Optional[float] = None
    web_thickness: Optional[float] = None
    area: Optional[float] = None
    moment_of_inertia: Optional[float] = None
    section_modulus: Optional[float] = None
    
    def __post_init__(self):
        """Calculate derived properties if not provided."""
        if self.area is None:
            self.area = self.width * self.height
        
        if self.moment_of_inertia is None:
            # Rectangular section: I = bh³/12
            self.moment_of_inertia = (self.width * self.height ** 3) / 12
        
        if self.section_modulus is None:
            # Z = I / y_max
            self.section_modulus = self.moment_of_inertia / (self.height / 2)


@dataclass
class LoadCase:
    """
    Load case definition.
    
    Attributes:
        load_type: Type of load
        magnitude: Load magnitude (kN/m for distributed, kN for point)
        position: Position of point load (m from left support)
        load_factor: Load factor for design
    """
    load_type: LoadType
    magnitude: float  # kN/m or kN
    position: Optional[float] = None  # For point loads
    load_factor: float = 1.0


@dataclass
class BeamAnalysisResult:
    """
    Results of beam analysis.
    
    Attributes:
        max_moment: Maximum bending moment (kN·m)
        max_shear: Maximum shear force (kN)
        max_deflection: Maximum deflection (mm)
        max_stress: Maximum bending stress (MPa)
        critical_location: Location of maximum moment (m)
        reactions: Support reactions (kN)
        is_safe: Safety check result
        utilization_ratio: Load/capacity ratio
    """
    max_moment: float  # kN·m
    max_shear: float  # kN
    max_deflection: float  # mm
    max_stress: float  # MPa
    critical_location: float  # m
    reactions: Dict[str, float]  # kN
    is_safe: bool
    utilization_ratio: float


class StructuralSolver:
    """
    Main structural analysis engine.
    
    Provides comprehensive structural calculations including:
    - Load analysis
    - Beam design
    - Column design
    - Safety verification
    """
    
    # Load factors as per design codes (simplified)
    LOAD_FACTORS = {
        LoadType.DEAD: 1.4,
        LoadType.LIVE: 1.6,
        LoadType.WIND: 1.4,
        LoadType.SEISMIC: 1.0,
        LoadType.SNOW: 1.5,
    }
    
    @staticmethod
    def calculate_dead_load(
        floor_area: float,  # m²
        floor_thickness: float,  # mm
        material: MaterialProperties,
        finishes_load: float = 1.0,  # kN/m²
    ) -> float:
        """
        Calculate dead load from floor slab.
        
        Formula: DL = γ × t × A + finishes × A
        
        where:
        - γ = unit weight of material
        - t = thickness
        - A = area
        - finishes = additional loads (tiles, screed, etc.)
        
        Args:
            floor_area: Floor area (m²)
            floor_thickness: Slab thickness (mm)
            material: Material properties
            finishes_load: Additional finishes load (kN/m²)
            
        Returns:
            float: Total dead load (kN)
        """
        # Convert thickness to meters
        thickness_m = floor_thickness / 1000
        
        # Self-weight
        self_weight = material.unit_weight * thickness_m * floor_area
        
        # Finishes
        finishes = finishes_load * floor_area
        
        return self_weight + finishes
    
    @staticmethod
    def calculate_live_load(
        floor_area: float,  # m²
        occupancy_type: str = "residential",
    ) -> float:
        """
        Calculate live load based on occupancy type.
        
        Args:
            floor_area: Floor area (m²)
            occupancy_type: Type of occupancy
            
        Returns:
            float: Total live load (kN)
        """
        # Live load intensities (kN/m²) based on occupancy
        live_loads = {
            "residential": 2.0,
            "office": 3.0,
            "commercial": 4.0,
            "industrial": 5.0,
            "storage": 7.5,
            "parking": 4.0,
            "roof": 1.5,
        }
        
        intensity = live_loads.get(occupancy_type, 2.0)
        
        return intensity * floor_area
    
    @staticmethod
    def calculate_beam_reactions(
        span: float,  # m
        load_cases: List[LoadCase],
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
    ) -> Dict[str, float]:
        """
        Calculate support reactions for a beam.
        
        For simply supported beam with UDL:
        R_A = R_B = wL/2
        
        For simply supported beam with point load at distance 'a':
        R_A = P(L-a)/L
        R_B = Pa/L
        
        Args:
            span: Beam span (m)
            load_cases: List of load cases
            support_type: Type of beam support
            
        Returns:
            Dict[str, float]: Support reactions
        """
        total_reaction_left = 0.0
        total_reaction_right = 0.0
        
        for load in load_cases:
            factored_load = load.magnitude * load.load_factor
            
            if load.position is None:
                # Distributed load
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    total_reaction_left += factored_load * span / 2
                    total_reaction_right += factored_load * span / 2
                elif support_type == SupportType.CANTILEVER:
                    total_reaction_left += factored_load * span
                elif support_type == SupportType.FIXED:
                    total_reaction_left += factored_load * span / 2
                    total_reaction_right += factored_load * span / 2
            else:
                # Point load
                a = load.position
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    total_reaction_left += factored_load * (span - a) / span
                    total_reaction_right += factored_load * a / span
                elif support_type == SupportType.CANTILEVER:
                    total_reaction_left += factored_load
        
        return {
            "left": round(total_reaction_left, 2),
            "right": round(total_reaction_right, 2),
        }
    
    @staticmethod
    def calculate_bending_moment(
        span: float,  # m
        load_cases: List[LoadCase],
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
    ) -> Tuple[float, float]:
        """
        Calculate maximum bending moment.
        
        For simply supported beam with UDL:
        M_max = wL²/8 at mid-span
        
        For simply supported beam with point load at center:
        M_max = PL/4 at center
        
        For cantilever with UDL:
        M_max = wL²/2 at fixed end
        
        For fixed beam with UDL:
        M_max = wL²/12 at supports, wL²/24 at mid-span
        
        Args:
            span: Beam span (m)
            load_cases: List of load cases
            support_type: Type of beam support
            
        Returns:
            Tuple[float, float]: (max_moment, critical_location)
        """
        total_moment = 0.0
        critical_location = span / 2  # Default
        
        for load in load_cases:
            factored_load = load.magnitude * load.load_factor
            
            if load.position is None:
                # Distributed load
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    total_moment += factored_load * span ** 2 / 8
                    critical_location = span / 2
                elif support_type == SupportType.CANTILEVER:
                    total_moment += factored_load * span ** 2 / 2
                    critical_location = 0  # At fixed end
                elif support_type == SupportType.FIXED:
                    total_moment += factored_load * span ** 2 / 12
                    critical_location = 0  # At supports
            else:
                # Point load
                a = load.position
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    # M = Pab/L at point load location
                    b = span - a
                    total_moment += factored_load * a * b / span
                    critical_location = a
                elif support_type == SupportType.CANTILEVER:
                    total_moment += factored_load * (span - a)
                    critical_location = 0
        
        return round(total_moment, 2), round(critical_location, 2)
    
    @staticmethod
    def calculate_shear_force(
        span: float,  # m
        load_cases: List[LoadCase],
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
    ) -> float:
        """
        Calculate maximum shear force.
        
        For simply supported beam with UDL:
        V_max = wL/2 at supports
        
        For cantilever with UDL:
        V_max = wL at fixed end
        
        Args:
            span: Beam span (m)
            load_cases: List of load cases
            support_type: Type of beam support
            
        Returns:
            float: Maximum shear force (kN)
        """
        total_shear = 0.0
        
        for load in load_cases:
            factored_load = load.magnitude * load.load_factor
            
            if load.position is None:
                # Distributed load
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    total_shear += factored_load * span / 2
                elif support_type == SupportType.CANTILEVER:
                    total_shear += factored_load * span
                elif support_type == SupportType.FIXED:
                    total_shear += factored_load * span / 2
            else:
                # Point load
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    a = load.position
                    total_shear += max(
                        factored_load * (span - a) / span,
                        factored_load * a / span
                    )
                elif support_type == SupportType.CANTILEVER:
                    total_shear += factored_load
        
        return round(total_shear, 2)
    
    @staticmethod
    def calculate_deflection(
        span: float,  # m
        load_cases: List[LoadCase],
        beam: BeamProperties,
        material: MaterialProperties,
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
    ) -> float:
        """
        Calculate maximum deflection.
        
        For simply supported beam with UDL:
        δ_max = 5wL⁴/(384EI)
        
        For simply supported beam with point load at center:
        δ_max = PL³/(48EI)
        
        For cantilever with UDL:
        δ_max = wL⁴/(8EI)
        
        Args:
            span: Beam span (m)
            load_cases: List of load cases
            beam: Beam properties
            material: Material properties
            support_type: Type of beam support
            
        Returns:
            float: Maximum deflection (mm)
        """
        # Convert to consistent units
        E = material.elastic_modulus * 1e6  # GPa to kN/mm²
        I = beam.moment_of_inertia  # mm⁴
        L = span * 1000  # m to mm
        
        total_deflection = 0.0
        
        for load in load_cases:
            # Use unfactored loads for deflection (serviceability)
            w = load.magnitude  # kN/m
            
            if load.position is None:
                # Distributed load
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    # δ = 5wL⁴/(384EI)
                    # w in kN/m = kN/(1000mm) = w/1000 kN/mm
                    w_mm = w / 1000
                    total_deflection += (
                        5 * w_mm * L ** 4 / (384 * E * I)
                    )
                elif support_type == SupportType.CANTILEVER:
                    w_mm = w / 1000
                    total_deflection += w_mm * L ** 4 / (8 * E * I)
                elif support_type == SupportType.FIXED:
                    w_mm = w / 1000
                    total_deflection += w_mm * L ** 4 / (384 * E * I)
            else:
                # Point load
                P = load.magnitude  # kN
                if support_type == SupportType.SIMPLY_SUPPORTED:
                    a = load.position * 1000  # mm
                    b = L - a
                    # δ = Pab(3L²-4b²)/(27EIL) simplified for center load
                    if abs(a - L/2) < 0.1 * L:  # Near center
                        total_deflection += P * L ** 3 / (48 * E * I)
                    else:
                        # General formula
                        total_deflection += (
                            P * a * b * (3 * L ** 2 - 4 * b ** 2) / (27 * E * I * L)
                        )
                elif support_type == SupportType.CANTILEVER:
                    a = load.position * 1000
                    total_deflection += P * a ** 2 * (3 * L - a) / (6 * E * I)
        
        return round(total_deflection, 2)
    
    @staticmethod
    def calculate_bending_stress(
        moment: float,  # kN·m
        beam: BeamProperties,
    ) -> float:
        """
        Calculate bending stress.
        
        Formula: σ = M/Z
        
        where:
        - M = bending moment
        - Z = section modulus
        
        Args:
            moment: Bending moment (kN·m)
            beam: Beam properties
            
        Returns:
            float: Bending stress (MPa)
        """
        # Convert moment to kN·mm
        M = moment * 1000  # kN·m to kN·mm
        Z = beam.section_modulus  # mm³
        
        stress = M / Z  # kN/mm² = MPa
        
        return round(stress, 2)
    
    @staticmethod
    def analyze_beam(
        span: float,
        load_cases: List[LoadCase],
        beam: BeamProperties,
        material: MaterialProperties,
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
        deflection_limit: float = 0.003,  # L/360
    ) -> BeamAnalysisResult:
        """
        Comprehensive beam analysis.
        
        Args:
            span: Beam span (m)
            load_cases: List of load cases
            beam: Beam properties
            material: Material properties
            support_type: Type of beam support
            deflection_limit: Allowable deflection ratio (default L/360)
            
        Returns:
            BeamAnalysisResult: Complete analysis results
        """
        # Calculate reactions
        reactions = StructuralSolver.calculate_beam_reactions(
            span, load_cases, support_type
        )
        
        # Calculate bending moment
        max_moment, critical_location = StructuralSolver.calculate_bending_moment(
            span, load_cases, support_type
        )
        
        # Calculate shear force
        max_shear = StructuralSolver.calculate_shear_force(
            span, load_cases, support_type
        )
        
        # Calculate deflection (using unfactored loads)
        unfactored_loads = [
            LoadCase(
                load_type=lc.load_type,
                magnitude=lc.magnitude,
                position=lc.position,
                load_factor=1.0,
            )
            for lc in load_cases
        ]
        max_deflection = StructuralSolver.calculate_deflection(
            span, unfactored_loads, beam, material, support_type
        )
        
        # Calculate bending stress
        max_stress = StructuralSolver.calculate_bending_stress(max_moment, beam)
        
        # Check safety
        allowable_stress = material.yield_strength if material.yield_strength > 0 else material.tensile_strength
        stress_ratio = max_stress / allowable_stress
        
        allowable_deflection = span * 1000 * deflection_limit  # mm
        deflection_ratio = max_deflection / allowable_deflection
        
        utilization_ratio = max(stress_ratio, deflection_ratio)
        is_safe = utilization_ratio <= 1.0
        
        return BeamAnalysisResult(
            max_moment=max_moment,
            max_shear=max_shear,
            max_deflection=max_deflection,
            max_stress=max_stress,
            critical_location=critical_location,
            reactions=reactions,
            is_safe=is_safe,
            utilization_ratio=round(utilization_ratio, 3),
        )
    
    @staticmethod
    def design_beam_section(
        span: float,
        total_load: float,  # kN/m
        material: MaterialProperties,
        support_type: SupportType = SupportType.SIMPLY_SUPPORTED,
        depth_to_span_ratio: float = 0.02,
        width_to_depth_ratio: float = 0.5,
    ) -> BeamProperties:
        """
        Design beam section based on loading.
        
        Args:
            span: Beam span (m)
            total_load: Total factored load (kN/m)
            material: Material properties
            support_type: Type of beam support
            depth_to_span_ratio: L/d ratio (default 1/50)
            width_to_depth_ratio: b/d ratio (default 0.5)
            
        Returns:
            BeamProperties: Designed beam section
        """
        # Estimate depth based on span
        estimated_depth = span * 1000 * depth_to_span_ratio  # mm
        
        # Estimate width
        estimated_width = estimated_depth * width_to_depth_ratio  # mm
        
        # Round to nearest 25mm
        height = round(estimated_depth / 25) * 25
        width = round(estimated_width / 25) * 25
        
        # Minimum dimensions
        height = max(height, 200)  # Minimum 200mm
        width = max(width, 150)  # Minimum 150mm
        
        return BeamProperties(width=width, height=height)
    
    @staticmethod
    def calculate_column_load(
        tributary_area: float,  # m²
        num_floors: int,
        dead_load_intensity: float = 12.0,  # kN/m²
        live_load_intensity: float = 3.0,  # kN/m²
        live_load_reduction: float = 0.0,
    ) -> float:
        """
        Calculate column axial load.
        
        Formula: P = (DL + LL × reduction) × A × n
        
        Args:
            tributary_area: Tributary area per floor (m²)
            num_floors: Number of floors supported
            dead_load_intensity: Average dead load (kN/m²)
            live_load_intensity: Average live load (kN/m²)
            live_load_reduction: Live load reduction factor
            
        Returns:
            float: Total column load (kN)
        """
        factored_dead = dead_load_intensity * 1.4
        factored_live = live_load_intensity * 1.6 * (1 - live_load_reduction)
        
        total_load = (factored_dead + factored_live) * tributary_area * num_floors
        
        return round(total_load, 2)
    
    @staticmethod
    def check_column_capacity(
        axial_load: float,  # kN
        column_area: float,  # mm²
        material: MaterialProperties,
        effective_length: float,  # m
        slenderness_limit: float = 12.0,
    ) -> Tuple[bool, float, List[str]]:
        """
        Check column capacity.
        
        Simplified check based on:
        1. Axial stress check
        2. Slenderness check
        
        Args:
            axial_load: Factored axial load (kN)
            column_area: Cross-sectional area (mm²)
            material: Material properties
            effective_length: Effective length (m)
            slenderness_limit: Maximum slenderness ratio
            
        Returns:
            Tuple containing:
            - bool: Is safe
            - float: Utilization ratio
            - List[str]: Warnings/notes
        """
        notes: List[str] = []
        
        # Axial stress
        axial_stress = (axial_load * 1000) / column_area  # MPa
        
        # Allowable stress (simplified)
        if material.yield_strength > 0:
            allowable_stress = material.yield_strength * 0.6  # 60% for columns
        else:
            allowable_stress = material.compressive_strength * 0.4
        
        stress_ratio = axial_stress / allowable_stress
        
        # Slenderness check (simplified)
        # For concrete columns: λ = Le/b
        # Assuming square column
        side = np.sqrt(column_area)
        slenderness = (effective_length * 1000) / side
        
        if slenderness > slenderness_limit:
            notes.append(f"High slenderness ratio ({slenderness:.1f}) - consider lateral ties")
            slenderness_factor = slenderness_limit / slenderness
        else:
            slenderness_factor = 1.0
        
        utilization = stress_ratio / slenderness_factor
        is_safe = utilization <= 1.0
        
        if not is_safe:
            notes.append(f"Column overstressed (utilization: {utilization:.2%})")
        
        return is_safe, round(utilization, 3), notes
    
    @staticmethod
    def calculate_structural_scores(
        beam_result: BeamAnalysisResult,
        column_utilization: float,
        foundation_settlement: float,
    ) -> Dict[str, float]:
        """
        Calculate overall structural scores.
        
        Args:
            beam_result: Beam analysis result
            column_utilization: Column utilization ratio
            foundation_settlement: Estimated settlement (mm)
            
        Returns:
            Dict[str, float]: Structural scores (0-100)
        """
        # Safety score (based on utilization)
        max_utilization = max(beam_result.utilization_ratio, column_utilization)
        safety_score = max(0, 100 * (1 - max_utilization))
        
        # Stability score (based on deflection and settlement)
        deflection_penalty = min(beam_result.max_deflection / 20, 1) * 30
        settlement_penalty = min(foundation_settlement / 25, 1) * 30
        stability_score = max(0, 100 - deflection_penalty - settlement_penalty)
        
        # Material efficiency (optimal utilization around 0.7-0.85)
        avg_utilization = (beam_result.utilization_ratio + column_utilization) / 2
        if 0.6 <= avg_utilization <= 0.85:
            efficiency_score = 100
        elif avg_utilization < 0.6:
            efficiency_score = 100 * avg_utilization / 0.6
        else:
            efficiency_score = max(0, 100 * (1 - avg_utilization) / 0.15)
        
        return {
            "safety_score": round(safety_score, 1),
            "stability_score": round(stability_score, 1),
            "material_efficiency_score": round(efficiency_score, 1),
        }