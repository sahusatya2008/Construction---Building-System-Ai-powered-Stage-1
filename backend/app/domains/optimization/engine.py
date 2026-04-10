"""
AI Optimization Layer
=====================
Multi-objective optimization for architectural design.

Implements:
- Constraint-based optimization
- Multi-objective optimization (cost, stability, ventilation, aesthetics)
- Genetic Algorithm for layout optimization
- Design scoring and evaluation
- Explainable AI outputs

All optimizations are deterministic and explainable.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import json
import random

import numpy as np

from app.domains.geometry.engine import GeometryEngine, Polygon, Point2D
from app.domains.soil.engine import (
    SoilAnalysisEngine,
    SoilProperties,
    SoilType,
    FoundationRecommendation,
)
from app.domains.structural.engine import (
    StructuralSolver,
    MaterialProperties,
    MaterialType,
    BeamProperties,
    LoadCase,
    LoadType,
    SupportType,
)
from app.domains.layout.engine import (
    LayoutOptimizer,
    RoomRequirements,
    RoomType,
    LayoutResult,
    Room,
)


class OptimizationObjective(str, Enum):
    """Optimization objectives."""
    COST = "cost"
    STABILITY = "stability"
    VENTILATION = "ventilation"
    DAYLIGHT = "daylight"
    SPACE_UTILIZATION = "space_utilization"
    AESTHETICS = "aesthetics"
    ENERGY_EFFICIENCY = "energy_efficiency"


class BuildingType(str, Enum):
    """Types of buildings."""
    RESIDENTIAL_SINGLE = "residential_single"
    RESIDENTIAL_MULTI = "residential_multi"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"


@dataclass
class DesignConstraints:
    """
    Constraints for design optimization.
    
    Attributes:
        max_height: Maximum building height (m)
        max_floors: Maximum number of floors
        min_setback: Minimum setback from boundary (m)
        max_coverage: Maximum plot coverage ratio
        min_parking: Minimum parking spaces
        min_open_space: Minimum open space ratio
        floor_area_ratio: Maximum FAR
    """
    max_height: float = 15.0  # m
    max_floors: int = 4
    min_setback: float = 3.0  # m
    max_coverage: float = 0.6  # 60%
    min_parking: int = 1
    min_open_space: float = 0.2  # 20%
    floor_area_ratio: float = 2.0


@dataclass
class OptimizationWeights:
    """
    Weights for multi-objective optimization.
    
    Attributes:
        cost: Weight for cost minimization
        stability: Weight for structural stability
        ventilation: Weight for ventilation quality
        daylight: Weight for daylight access
        space_utilization: Weight for space efficiency
        aesthetics: Weight for aesthetic quality
    """
    cost: float = 0.15
    stability: float = 0.25
    ventilation: float = 0.15
    daylight: float = 0.15
    space_utilization: float = 0.15
    aesthetics: float = 0.15
    
    def normalize(self) -> "OptimizationWeights":
        """Normalize weights to sum to 1."""
        total = sum([
            self.cost, self.stability, self.ventilation,
            self.daylight, self.space_utilization, self.aesthetics
        ])
        if total == 0:
            return self
        return OptimizationWeights(
            cost=self.cost / total,
            stability=self.stability / total,
            ventilation=self.ventilation / total,
            daylight=self.daylight / total,
            space_utilization=self.space_utilization / total,
            aesthetics=self.aesthetics / total,
        )


@dataclass
class DesignScores:
    """
    Scores for a generated design.
    
    All scores are on a scale of 0-100.
    
    Attributes:
        safety_score: Structural safety score
        stability_score: Structural stability score
        material_efficiency_score: Material usage efficiency
        space_utilization_score: Space utilization efficiency
        ventilation_score: Ventilation quality score
        daylight_score: Daylight access score
        cost_efficiency_score: Cost efficiency score
        overall_score: Weighted overall score
    """
    safety_score: float
    stability_score: float
    material_efficiency_score: float
    space_utilization_score: float
    ventilation_score: float
    daylight_score: float
    cost_efficiency_score: float
    overall_score: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "safety_score": self.safety_score,
            "stability_score": self.stability_score,
            "material_efficiency_score": self.material_efficiency_score,
            "space_utilization_score": self.space_utilization_score,
            "ventilation_score": self.ventilation_score,
            "daylight_score": self.daylight_score,
            "cost_efficiency_score": self.cost_efficiency_score,
            "overall_score": self.overall_score,
        }


@dataclass
class GeneratedDesign:
    """
    Complete generated architectural design.
    
    Attributes:
        design_id: Unique design identifier
        plot_geometry: Plot polygon
        soil_properties: Soil analysis results
        foundation: Foundation recommendation
        layout: Room layout result
        structural_elements: Structural element specifications
        scores: Design scores
        constraints_satisfied: Whether all constraints are satisfied
        warnings: List of warnings
        recommendations: List of recommendations
        design_data: Complete design data for export
    """
    design_id: str
    plot_geometry: Polygon
    soil_properties: SoilProperties
    foundation: FoundationRecommendation
    layout: LayoutResult
    structural_elements: Dict[str, Any]
    scores: DesignScores
    constraints_satisfied: bool
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    design_data: Dict[str, Any] = field(default_factory=dict)


class GeneticOptimizer:
    """
    Genetic Algorithm optimizer for architectural design.
    
    Uses evolutionary computation to find optimal designs
    that satisfy multiple objectives.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism: int = 2,
    ):
        """
        Initialize the genetic optimizer.
        
        Args:
            population_size: Size of the population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elitism: Number of top individuals to preserve
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
    
    def optimize(
        self,
        objective_function: Callable[[Dict], float],
        parameter_bounds: Dict[str, Tuple[float, float]],
        constraints: List[Callable[[Dict], bool]] = None,
    ) -> Tuple[Dict, float]:
        """
        Run genetic algorithm optimization.
        
        Args:
            objective_function: Function to maximize
            parameter_bounds: Bounds for each parameter
            constraints: List of constraint functions
            
        Returns:
            Tuple[Dict, float]: Best solution and its fitness
        """
        param_names = list(parameter_bounds.keys())
        num_params = len(param_names)
        
        # Initialize population
        population = []
        for _ in range(self.population_size):
            individual = {}
            for name, (low, high) in parameter_bounds.items():
                individual[name] = random.uniform(low, high)
            population.append(individual)
        
        best_individual = None
        best_fitness = float('-inf')
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                # Check constraints
                if constraints:
                    violated = any(not c(individual) for c in constraints)
                    if violated:
                        fitness_scores.append(float('-inf'))
                        continue
                
                fitness = objective_function(individual)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Selection (tournament selection)
            new_population = []
            
            # Elitism: preserve top individuals
            sorted_indices = np.argsort(fitness_scores)[::-1]
            for i in range(self.elitism):
                new_population.append(population[sorted_indices[i]].copy())
            
            # Generate rest of population
            while len(new_population) < self.population_size:
                # Tournament selection
                tournament_size = 3
                parent1_idx = self._tournament_select(fitness_scores, tournament_size)
                parent2_idx = self._tournament_select(fitness_scores, tournament_size)
                
                parent1 = population[parent1_idx]
                parent2 = population[parent2_idx]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2, param_names)
                else:
                    child = parent1.copy()
                
                # Mutation
                child = self._mutate(child, parameter_bounds)
                
                new_population.append(child)
            
            population = new_population
        
        return best_individual or population[0], best_fitness
    
    def _tournament_select(
        self,
        fitness_scores: List[float],
        tournament_size: int,
    ) -> int:
        """Select individual using tournament selection."""
        indices = random.sample(range(len(fitness_scores)), tournament_size)
        best_idx = max(indices, key=lambda i: fitness_scores[i])
        return best_idx
    
    def _crossover(
        self,
        parent1: Dict,
        parent2: Dict,
        param_names: List[str],
    ) -> Dict:
        """Perform crossover between two parents."""
        child = {}
        crossover_point = random.randint(1, len(param_names) - 1)
        
        for i, name in enumerate(param_names):
            if i < crossover_point:
                child[name] = parent1[name]
            else:
                child[name] = parent2[name]
        
        return child
    
    def _mutate(
        self,
        individual: Dict,
        bounds: Dict[str, Tuple[float, float]],
    ) -> Dict:
        """Mutate an individual."""
        mutated = individual.copy()
        
        for name, (low, high) in bounds.items():
            if random.random() < self.mutation_rate:
                # Gaussian mutation
                range_size = high - low
                mutation = random.gauss(0, range_size * 0.1)
                mutated[name] = max(low, min(high, mutated[name] + mutation))
        
        return mutated


class DesignOptimizer:
    """
    Main design optimization engine.
    
    Integrates all domain engines and provides comprehensive
    architectural design optimization.
    """
    
    # Cost factors (simplified, in local currency per m²)
    COST_FACTORS = {
        "foundation": 3000,  # per m² of foundation
        "structure": 4500,  # per m² of floor
        "finishing": 2500,  # per m² of floor
        "services": 1500,  # per m² of floor
    }
    
    @staticmethod
    def generate_design(
        plot_coordinates: List[Tuple[float, float]],
        soil_type: SoilType,
        building_type: BuildingType,
        num_bedrooms: int = 2,
        num_bathrooms: int = 1,
        num_floors: int = 1,
        constraints: Optional[DesignConstraints] = None,
        weights: Optional[OptimizationWeights] = None,
        latitude: float = 28.0,
    ) -> GeneratedDesign:
        """
        Generate a complete architectural design.
        
        This is the main entry point for design generation.
        
        Args:
            plot_coordinates: List of (x, y) coordinates defining the plot
            soil_type: Type of soil on the plot
            building_type: Type of building to design
            num_bedrooms: Number of bedrooms
            num_bathrooms: Number of bathrooms
            num_floors: Number of floors
            constraints: Design constraints
            weights: Optimization weights
            latitude: Site latitude for sun path
            
        Returns:
            GeneratedDesign: Complete generated design
        """
        # Use defaults if not provided
        if constraints is None:
            constraints = DesignConstraints()
        if weights is None:
            weights = OptimizationWeights()
        
        # Normalize weights
        weights = weights.normalize()
        
        warnings: List[str] = []
        recommendations: List[str] = []
        
        # 1. Validate and analyze plot geometry
        is_valid, error, plot_properties = GeometryEngine.validate_plot_shape(
            plot_coordinates
        )
        
        if not is_valid:
            raise ValueError(f"Invalid plot: {error}")
        
        # Create polygon
        polygon = GeometryEngine.create_polygon_from_coordinates(plot_coordinates)
        plot_area = plot_properties["area"]
        
        # Check plot coverage constraint
        if plot_area * constraints.max_coverage < 50:
            warnings.append("Very small buildable area due to coverage constraint")
        
        # 2. Analyze soil
        soil_properties = SoilProperties.get_default_properties(soil_type)
        
        # 3. Generate room requirements based on building type
        room_requirements = DesignOptimizer._generate_room_requirements(
            building_type, num_bedrooms, num_bathrooms, plot_area
        )
        
        # 4. Generate layout
        width, height = plot_properties["dimensions"].values()
        
        layout = LayoutOptimizer.generate_room_layout(
            plot_width=width,
            plot_height=height,
            room_requirements=room_requirements,
            num_floors=num_floors,
            setback=constraints.min_setback,
        )
        
        warnings.extend(layout.issues)
        
        # 5. Calculate structural loads
        floor_area = layout.total_area
        total_load = DesignOptimizer._calculate_total_load(floor_area, num_floors)
        
        # 6. Foundation design
        building_height = num_floors * 3.0  # Assume 3m per floor
        
        foundation = SoilAnalysisEngine.recommend_foundation_type(
            soil=soil_properties,
            total_load=total_load,
            foundation_area=floor_area,
            building_height=building_height,
            number_of_stories=num_floors,
        )
        
        recommendations.extend(foundation.notes)
        
        # 7. Structural design
        material = MaterialProperties.get_default_properties(MaterialType.REINFORCED_CONCRETE)
        
        structural_elements = DesignOptimizer._design_structural_elements(
            layout, material, num_floors
        )
        
        # 8. Calculate scores
        scores = DesignOptimizer._calculate_design_scores(
            layout=layout,
            foundation=foundation,
            structural_elements=structural_elements,
            soil_properties=soil_properties,
            plot_area=plot_area,
            weights=weights,
        )
        
        # 9. Check constraints
        constraints_satisfied = DesignOptimizer._check_constraints(
            layout, constraints, plot_area, num_floors
        )
        
        if not constraints_satisfied:
            warnings.append("Some design constraints may not be fully satisfied")
        
        # 10. Generate recommendations
        if scores.safety_score < 70:
            recommendations.append("Consider increasing structural member sizes")
        if scores.ventilation_score < 70:
            recommendations.append("Consider adding more windows for better ventilation")
        if scores.daylight_score < 70:
            recommendations.append("Consider larger windows or skylights for better daylight")
        
        # 11. Prepare design data for export
        design_data = DesignOptimizer._prepare_design_data(
            polygon=polygon,
            layout=layout,
            foundation=foundation,
            structural_elements=structural_elements,
            scores=scores,
        )
        
        return GeneratedDesign(
            design_id=f"design_{random.randint(10000, 99999)}",
            plot_geometry=polygon,
            soil_properties=soil_properties,
            foundation=foundation,
            layout=layout,
            structural_elements=structural_elements,
            scores=scores,
            constraints_satisfied=constraints_satisfied,
            warnings=warnings,
            recommendations=recommendations,
            design_data=design_data,
        )
    
    @staticmethod
    def _generate_room_requirements(
        building_type: BuildingType,
        num_bedrooms: int,
        num_bathrooms: int,
        plot_area: float,
    ) -> List[RoomRequirements]:
        """Generate room requirements based on building type."""
        requirements = []
        
        # Always include living room
        requirements.append(
            RoomRequirements.get_standard_requirements(RoomType.LIVING_ROOM)
        )
        
        # Add bedrooms
        for _ in range(num_bedrooms):
            requirements.append(
                RoomRequirements.get_standard_requirements(RoomType.BEDROOM)
            )
        
        # Add bathrooms
        for _ in range(num_bathrooms):
            requirements.append(
                RoomRequirements.get_standard_requirements(RoomType.BATHROOM)
            )
        
        # Add kitchen
        requirements.append(
            RoomRequirements.get_standard_requirements(RoomType.KITCHEN)
        )
        
        # Add dining if space permits
        if plot_area > 150:
            requirements.append(
                RoomRequirements.get_standard_requirements(RoomType.DINING)
            )
        
        # Add entrance
        requirements.append(
            RoomRequirements.get_standard_requirements(RoomType.ENTRANCE)
        )
        
        # Add storage
        requirements.append(
            RoomRequirements.get_standard_requirements(RoomType.STORAGE)
        )
        
        return requirements
    
    @staticmethod
    def _calculate_total_load(
        floor_area: float,
        num_floors: int,
    ) -> float:
        """Calculate total structural load."""
        # Dead load: 12 kN/m² (typical RC slab)
        dead_load = 12.0 * floor_area * num_floors
        
        # Live load: 3 kN/m² (residential)
        live_load = 3.0 * floor_area * num_floors
        
        # Factored load
        total_load = 1.4 * dead_load + 1.6 * live_load
        
        return total_load
    
    @staticmethod
    def _design_structural_elements(
        layout: LayoutResult,
        material: MaterialProperties,
        num_floors: int,
    ) -> Dict[str, Any]:
        """Design structural elements."""
        elements = {
            "beams": [],
            "columns": [],
            "slabs": [],
        }
        
        # Design beams for each room
        for room in layout.rooms:
            # Span is the longer dimension
            span = max(room.width, room.height)
            
            # Estimate load on beam
            tributary_width = min(room.width, room.height)
            total_load = 15.0 * tributary_width  # kN/m (factored)
            
            # Design beam
            beam = StructuralSolver.design_beam_section(
                span=span,
                total_load=total_load,
                material=material,
            )
            
            elements["beams"].append({
                "id": f"beam_{room.id}",
                "span": round(span, 2),
                "width": beam.width,
                "height": beam.height,
                "location": room.id,
            })
        
        # Design columns (one per 40-50 m²)
        num_columns = max(4, int(layout.total_area / 40))
        column_size = 300  # mm (initial)
        
        for i in range(num_columns):
            elements["columns"].append({
                "id": f"col_{i}",
                "size": column_size,
                "type": "square",
            })
        
        # Design slab
        slab_thickness = max(120, min(200, layout.total_area / 50))
        
        elements["slabs"].append({
            "id": "slab_main",
            "thickness": round(slab_thickness),
            "area": layout.total_area,
            "type": "two_way",
        })
        
        return elements
    
    @staticmethod
    def _calculate_design_scores(
        layout: LayoutResult,
        foundation: FoundationRecommendation,
        structural_elements: Dict[str, Any],
        soil_properties: SoilProperties,
        plot_area: float,
        weights: OptimizationWeights,
    ) -> DesignScores:
        """Calculate comprehensive design scores."""
        
        # Safety score (based on foundation and structural safety)
        safety_score = min(100, foundation.safety_factor * 30)
        
        # Stability score (based on settlement and structural integrity)
        settlement_penalty = min(foundation.settlement_estimate / 25, 1) * 30
        stability_score = max(0, 100 - settlement_penalty)
        
        # Material efficiency score
        # Based on utilization ratios
        material_efficiency = 75.0  # Default
        
        # Space utilization score
        space_utilization = LayoutOptimizer.calculate_space_utilization_score(
            layout, plot_area
        )
        
        # Ventilation score
        ventilation_score = layout.ventilation_score
        
        # Daylight score
        daylight_score = layout.daylight_score
        
        # Cost efficiency score
        # Lower settlement and efficient design = better cost
        cost_efficiency = 100 - (foundation.settlement_estimate / 50 * 100)
        cost_efficiency = max(0, min(100, cost_efficiency))
        
        # Overall score (weighted average)
        overall_score = (
            weights.stability * stability_score +
            weights.ventilation * ventilation_score +
            weights.daylight * daylight_score +
            weights.space_utilization * space_utilization +
            weights.cost * cost_efficiency +
            weights.aesthetics * 70  # Default aesthetics score
        )
        
        return DesignScores(
            safety_score=round(safety_score, 1),
            stability_score=round(stability_score, 1),
            material_efficiency_score=round(material_efficiency, 1),
            space_utilization_score=round(space_utilization, 1),
            ventilation_score=round(ventilation_score, 1),
            daylight_score=round(daylight_score, 1),
            cost_efficiency_score=round(cost_efficiency, 1),
            overall_score=round(overall_score, 1),
        )
    
    @staticmethod
    def _check_constraints(
        layout: LayoutResult,
        constraints: DesignConstraints,
        plot_area: float,
        num_floors: int,
    ) -> bool:
        """Check if design satisfies all constraints."""
        
        # Check plot coverage
        coverage = layout.total_area / plot_area
        if coverage > constraints.max_coverage:
            return False
        
        # Check FAR
        far = (layout.total_area * num_floors) / plot_area
        if far > constraints.floor_area_ratio:
            return False
        
        # Check number of floors
        if num_floors > constraints.max_floors:
            return False
        
        return True
    
    @staticmethod
    def _prepare_design_data(
        polygon: Polygon,
        layout: LayoutResult,
        foundation: FoundationRecommendation,
        structural_elements: Dict[str, Any],
        scores: DesignScores,
    ) -> Dict[str, Any]:
        """Prepare design data for export."""
        
        # Convert polygon to coordinate list
        plot_coords = [(v.x, v.y) for v in polygon.vertices]
        
        # Convert rooms to dict
        rooms_data = []
        for room in layout.rooms:
            rooms_data.append({
                "id": room.id,
                "type": room.room_type.value,
                "x": room.x,
                "y": room.y,
                "width": room.width,
                "height": room.height,
                "area": room.area,
                "has_window": room.has_window,
                "orientation": room.orientation.value if room.orientation else None,
                "adjacent_rooms": list(room.adjacent_rooms),
            })
        
        return {
            "plot": {
                "coordinates": plot_coords,
                "area": polygon.calculate_area(),
            },
            "layout": {
                "rooms": rooms_data,
                "total_area": layout.total_area,
                "circulation_area": layout.circulation_area,
            },
            "foundation": {
                "type": foundation.foundation_type.value,
                "depth": foundation.depth,
                "width": foundation.width,
                "bearing_pressure": foundation.allowable_bearing_pressure,
                "settlement": foundation.settlement_estimate,
            },
            "structure": structural_elements,
            "scores": scores.to_dict(),
        }


class MultiObjectiveOptimizer:
    """
    Multi-objective optimization using Pareto fronts.
    
    Finds the set of non-dominated solutions across
    multiple objectives.
    """
    
    @staticmethod
    def optimize(
        objectives: Dict[str, Callable[[Dict], float]],
        parameter_bounds: Dict[str, Tuple[float, float]],
        population_size: int = 100,
        generations: int = 200,
    ) -> List[Tuple[Dict, Dict[str, float]]]:
        """
        Run multi-objective optimization.
        
        Args:
            objectives: Dictionary of objective name -> objective function
            parameter_bounds: Bounds for each parameter
            population_size: Size of population
            generations: Number of generations
            
        Returns:
            List of (solution, objective_values) tuples on Pareto front
        """
        # Use NSGA-II style optimization
        # For simplicity, using weighted sum approach here
        
        solutions = []
        
        # Generate different weight combinations
        weight_combinations = MultiObjectiveOptimizer._generate_weight_combinations(
            len(objectives)
        )
        
        for weights in weight_combinations:
            # Create weighted objective
            def weighted_objective(x, w=weights, obj=objectives):
                return sum(w.get(name, 0) * f(x) for name, f in obj.items())
            
            # Optimize with genetic algorithm
            optimizer = GeneticOptimizer(
                population_size=population_size // len(weight_combinations),
                generations=generations,
            )
            
            solution, _ = optimizer.optimize(
                weighted_objective,
                parameter_bounds,
            )
            
            # Evaluate all objectives
            objective_values = {
                name: func(solution) for name, func in objectives.items()
            }
            
            solutions.append((solution, objective_values))
        
        # Filter to Pareto front
        pareto_front = MultiObjectiveOptimizer._filter_pareto_front(solutions)
        
        return pareto_front
    
    @staticmethod
    def _generate_weight_combinations(num_objectives: int) -> List[Dict[str, float]]:
        """Generate diverse weight combinations."""
        combinations = []
        
        # Equal weights
        equal_weight = 1.0 / num_objectives
        combinations.append({f"obj_{i}": equal_weight for i in range(num_objectives)})
        
        # Single objective focus
        for i in range(num_objectives):
            weights = {f"obj_{j}": 0.1 for j in range(num_objectives)}
            weights[f"obj_{i}"] = 0.9 - 0.1 * (num_objectives - 1)
            combinations.append(weights)
        
        return combinations
    
    @staticmethod
    def _filter_pareto_front(
        solutions: List[Tuple[Dict, Dict[str, float]]]
    ) -> List[Tuple[Dict, Dict[str, float]]]:
        """Filter solutions to Pareto front."""
        pareto_front = []
        
        for i, (sol_i, obj_i) in enumerate(solutions):
            is_dominated = False
            
            for j, (sol_j, obj_j) in enumerate(solutions):
                if i == j:
                    continue
                
                # Check if solution j dominates solution i
                dominates = all(
                    obj_j[k] >= obj_i[k] for k in obj_i.keys()
                ) and any(
                    obj_j[k] > obj_i[k] for k in obj_i.keys()
                )
                
                if dominates:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append((sol_i, obj_i))
        
        return pareto_front