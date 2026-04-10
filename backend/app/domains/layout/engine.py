"""
Layout Optimizer Module
=======================
AI-powered room layout optimization for architectural design.

Implements:
- Room adjacency graph modeling
- Space allocation optimization
- Ventilation flow analysis
- Sunlight/daylight simulation
- Circulation path optimization

Uses constraint-based optimization and graph algorithms.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import math

import numpy as np


class RoomType(str, Enum):
    """Types of rooms in a building."""
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    DINING = "dining"
    STUDY = "study"
    GARAGE = "garage"
    STORAGE = "storage"
    UTILITY = "utility"
    ENTRANCE = "entrance"
    CORRIDOR = "corridor"
    BALCONY = "balcony"


class Orientation(str, Enum):
    """Cardinal orientations."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"


@dataclass
class RoomRequirements:
    """
    Requirements for a room type.
    
    Attributes:
        room_type: Type of room
        min_area: Minimum area (m²)
        max_area: Maximum area (m²)
        min_width: Minimum width (m)
        min_natural_light: Minimum window area ratio
        requires_ventilation: Needs direct ventilation
        preferred_orientation: Preferred orientation for windows
        adjacency_requirements: Required adjacent rooms
        exclusion_requirements: Rooms to avoid adjacency
    """
    room_type: RoomType
    min_area: float  # m²
    max_area: float  # m²
    min_width: float = 2.4  # m
    min_natural_light: float = 0.1  # 10% of floor area
    requires_ventilation: bool = True
    preferred_orientation: Optional[Orientation] = None
    adjacency_requirements: Set[RoomType] = field(default_factory=set)
    exclusion_requirements: Set[RoomType] = field(default_factory=set)
    
    @classmethod
    def get_standard_requirements(cls, room_type: RoomType) -> "RoomRequirements":
        """Get standard requirements for a room type."""
        requirements = {
            RoomType.LIVING_ROOM: cls(
                room_type=room_type,
                min_area=12.0,
                max_area=40.0,
                min_width=3.0,
                min_natural_light=0.12,
                requires_ventilation=True,
                preferred_orientation=Orientation.SOUTH,
                adjacency_requirements={RoomType.DINING, RoomType.ENTRANCE},
                exclusion_requirements={RoomType.BATHROOM, RoomType.UTILITY},
            ),
            RoomType.BEDROOM: cls(
                room_type=room_type,
                min_area=9.0,
                max_area=25.0,
                min_width=2.7,
                min_natural_light=0.10,
                requires_ventilation=True,
                preferred_orientation=Orientation.SOUTH,
                exclusion_requirements={RoomType.KITCHEN, RoomType.BATHROOM},
            ),
            RoomType.KITCHEN: cls(
                room_type=room_type,
                min_area=6.0,
                max_area=20.0,
                min_width=2.0,
                min_natural_light=0.08,
                requires_ventilation=True,
                preferred_orientation=Orientation.EAST,
                adjacency_requirements={RoomType.DINING, RoomType.UTILITY},
                exclusion_requirements={RoomType.BEDROOM, RoomType.BATHROOM},
            ),
            RoomType.BATHROOM: cls(
                room_type=room_type,
                min_area=3.5,
                max_area=10.0,
                min_width=1.5,
                min_natural_light=0.05,
                requires_ventilation=True,
                preferred_orientation=Orientation.NORTH,
                adjacency_requirements={RoomType.BEDROOM},
            ),
            RoomType.DINING: cls(
                room_type=room_type,
                min_area=8.0,
                max_area=20.0,
                min_width=2.5,
                min_natural_light=0.10,
                requires_ventilation=True,
                preferred_orientation=Orientation.SOUTHEAST,
                adjacency_requirements={RoomType.KITCHEN, RoomType.LIVING_ROOM},
            ),
            RoomType.STUDY: cls(
                room_type=room_type,
                min_area=6.0,
                max_area=15.0,
                min_width=2.0,
                min_natural_light=0.10,
                requires_ventilation=True,
                preferred_orientation=Orientation.NORTH,
                exclusion_requirements={RoomType.KITCHEN, RoomType.BATHROOM},
            ),
            RoomType.ENTRANCE: cls(
                room_type=room_type,
                min_area=3.0,
                max_area=10.0,
                min_width=1.2,
                min_natural_light=0.05,
                requires_ventilation=True,
                adjacency_requirements={RoomType.LIVING_ROOM, RoomType.CORRIDOR},
            ),
            RoomType.CORRIDOR: cls(
                room_type=room_type,
                min_area=2.0,
                max_area=15.0,
                min_width=0.9,
                min_natural_light=0.0,
                requires_ventilation=False,
            ),
            RoomType.UTILITY: cls(
                room_type=room_type,
                min_area=2.0,
                max_area=8.0,
                min_width=1.5,
                min_natural_light=0.05,
                requires_ventilation=True,
                adjacency_requirements={RoomType.KITCHEN},
            ),
            RoomType.STORAGE: cls(
                room_type=room_type,
                min_area=1.5,
                max_area=10.0,
                min_width=0.8,
                min_natural_light=0.0,
                requires_ventilation=False,
            ),
            RoomType.GARAGE: cls(
                room_type=room_type,
                min_area=15.0,
                max_area=40.0,
                min_width=3.0,
                min_natural_light=0.0,
                requires_ventilation=True,
            ),
            RoomType.BALCONY: cls(
                room_type=room_type,
                min_area=3.0,
                max_area=15.0,
                min_width=1.0,
                min_natural_light=1.0,
                requires_ventilation=True,
                preferred_orientation=Orientation.SOUTH,
            ),
        }
        
        return requirements.get(room_type, requirements[RoomType.STORAGE])


@dataclass
class Room:
    """
    A room in the layout.
    
    Attributes:
        id: Unique room identifier
        room_type: Type of room
        x: X position (m)
        y: Y position (m)
        width: Room width (m)
        height: Room height (m)
        area: Room area (m²)
        orientation: Window orientation
        has_window: Has external window
        adjacent_rooms: IDs of adjacent rooms
    """
    id: str
    room_type: RoomType
    x: float  # m
    y: float  # m
    width: float  # m
    height: float  # m
    area: float  # m²
    orientation: Optional[Orientation] = None
    has_window: bool = False
    adjacent_rooms: Set[str] = field(default_factory=set)
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get room center coordinates."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def perimeter(self) -> float:
        """Get room perimeter."""
        return 2 * (self.width + self.height)
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio (width/height)."""
        return self.width / self.height if self.height > 0 else 0
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box (x_min, y_min, x_max, y_max)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def overlaps(self, other: "Room") -> bool:
        """Check if this room overlaps with another."""
        x1_min, y1_min, x1_max, y1_max = self.get_bounds()
        x2_min, y2_min, x2_max, y2_max = other.get_bounds()
        
        return not (
            x1_max <= x2_min or x2_max <= x1_min or
            y1_max <= y2_min or y2_max <= y1_min
        )
    
    def distance_to(self, other: "Room") -> float:
        """Calculate center-to-center distance to another room."""
        cx1, cy1 = self.center
        cx2, cy2 = other.center
        return math.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)


@dataclass
class LayoutResult:
    """
    Result of layout optimization.
    
    Attributes:
        rooms: List of placed rooms
        total_area: Total floor area (m²)
        circulation_area: Circulation space area (m²)
        space_utilization: Space utilization ratio
        adjacency_score: Room adjacency satisfaction score
        ventilation_score: Ventilation quality score
        daylight_score: Daylight access score
        overall_score: Overall layout quality score
        issues: List of issues/warnings
    """
    rooms: List[Room]
    total_area: float
    circulation_area: float
    space_utilization: float
    adjacency_score: float
    ventilation_score: float
    daylight_score: float
    overall_score: float
    issues: List[str] = field(default_factory=list)


class LayoutOptimizer:
    """
    Main layout optimization engine.
    
    Uses constraint-based optimization and graph algorithms
    to generate optimal room layouts.
    """
    
    # Minimum circulation width
    MIN_CORRIDOR_WIDTH = 0.9  # m
    
    # Wall thickness
    WALL_THICKNESS = 0.15  # m
    
    @staticmethod
    def calculate_sun_path(
        latitude: float,
        hour: int,
        day_of_year: int,
    ) -> Tuple[float, float]:
        """
        Calculate sun position (azimuth and altitude).
        
        Simplified sun position calculation.
        
        Formulas:
        δ = 23.45° × sin(360/365 × (284 + n))
        α = arcsin(sin(φ)×sin(δ) + cos(φ)×cos(δ)×cos(ω))
        A = arccos((sin(δ)×cos(φ) - cos(δ)×sin(φ)×cos(ω)) / cos(α))
        
        where:
        - δ = declination angle
        - φ = latitude
        - ω = hour angle
        - α = altitude
        - A = azimuth
        
        Args:
            latitude: Site latitude (degrees)
            hour: Hour of day (0-23)
            day_of_year: Day of year (1-365)
            
        Returns:
            Tuple[float, float]: (azimuth, altitude) in degrees
        """
        # Declination angle
        declination = 23.45 * math.sin(math.radians(360 / 365 * (284 + day_of_year)))
        
        # Hour angle (solar noon = 0)
        hour_angle = 15 * (hour - 12)  # 15 degrees per hour
        
        # Convert to radians
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)
        
        # Altitude
        sin_alt = (
            math.sin(lat_rad) * math.sin(dec_rad) +
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
        )
        altitude = math.degrees(math.asin(max(-1, min(1, sin_alt))))
        
        # Azimuth
        if altitude > 0:  # Sun is above horizon
            cos_az = (
                math.sin(dec_rad) * math.cos(lat_rad) -
                math.cos(dec_rad) * math.sin(lat_rad) * math.cos(hour_rad)
            ) / math.cos(math.radians(altitude))
            azimuth = math.degrees(math.acos(max(-1, min(1, cos_az))))
            if hour > 12:
                azimuth = 360 - azimuth
        else:
            azimuth = 0
        
        return azimuth, altitude
    
    @staticmethod
    def calculate_daylight_factor(
        room: Room,
        window_area: float,
        orientation: Orientation,
        latitude: float = 28.0,  # Default: New Delhi
    ) -> float:
        """
        Calculate average daylight factor for a room.
        
        Simplified daylight factor calculation:
        DF = (A_g × θ × τ) / (A × (1 - R²))
        
        where:
        - A_g = glazing area
        - θ = angle of visible sky
        - τ = light transmittance
        - A = room area
        - R = average reflectance
        
        Args:
            room: Room to analyze
            window_area: Window area (m²)
            orientation: Window orientation
            latitude: Site latitude
            
        Returns:
            float: Average daylight factor (%)
        """
        if window_area <= 0:
            return 0.0
        
        # Light transmittance (assuming double glazing)
        transmittance = 0.7
        
        # Angle of visible sky (assuming no obstructions)
        sky_angle = 60  # degrees
        
        # Average reflectance
        reflectance = 0.5
        
        # Orientation factor (South gets more light in northern hemisphere)
        orientation_factors = {
            Orientation.SOUTH: 1.2,
            Orientation.SOUTHEAST: 1.1,
            Orientation.SOUTHWEST: 1.1,
            Orientation.EAST: 0.9,
            Orientation.WEST: 0.9,
            Orientation.NORTHEAST: 0.7,
            Orientation.NORTHWEST: 0.7,
            Orientation.NORTH: 0.6,
        }
        
        orientation_factor = orientation_factors.get(orientation, 1.0)
        
        # Daylight factor
        df = (
            window_area
            * sky_angle
            * transmittance
            * orientation_factor
        ) / (room.area * (1 - reflectance ** 2))
        
        return round(df * 100, 2)  # Convert to percentage
    
    @staticmethod
    def calculate_ventilation_score(
        room: Room,
        has_cross_ventilation: bool,
        window_to_floor_ratio: float,
    ) -> float:
        """
        Calculate ventilation quality score.
        
        Based on:
        - Cross ventilation availability
        - Window-to-floor ratio
        - Room depth
        
        Args:
            room: Room to analyze
            has_cross_ventilation: Has windows on opposite walls
            window_to_floor_ratio: Window area / floor area
            
        Returns:
            float: Ventilation score (0-100)
        """
        score = 0.0
        
        # Cross ventilation bonus
        if has_cross_ventilation:
            score += 40
        
        # Window-to-floor ratio score
        # Optimal ratio is 10-20%
        if 0.10 <= window_to_floor_ratio <= 0.20:
            score += 30
        elif window_to_floor_ratio < 0.10:
            score += 30 * window_to_floor_ratio / 0.10
        else:
            score += max(0, 30 - (window_to_floor_ratio - 0.20) * 100)
        
        # Room depth score
        # Deeper rooms have poorer ventilation
        max_depth = max(room.width, room.height)
        if max_depth <= 6.0:
            score += 30
        else:
            score += max(0, 30 - (max_depth - 6.0) * 3)
        
        return round(score, 1)
    
    @staticmethod
    def check_adjacency_requirements(
        room: Room,
        all_rooms: List[Room],
        requirements: RoomRequirements,
    ) -> Tuple[float, List[str]]:
        """
        Check if adjacency requirements are satisfied.
        
        Args:
            room: Room to check
            all_rooms: All rooms in layout
            requirements: Room requirements
            
        Returns:
            Tuple[float, List[str]]: (score, issues)
        """
        issues = []
        score = 100.0
        
        # Get adjacent rooms
        adjacent_types = set()
        for other in all_rooms:
            if other.id != room.id and other.id in room.adjacent_rooms:
                adjacent_types.add(other.room_type)
        
        # Check required adjacencies
        for req_type in requirements.adjacency_requirements:
            if req_type not in adjacent_types:
                issues.append(f"Missing required adjacency to {req_type.value}")
                score -= 20
        
        # Check exclusion requirements
        for excl_type in requirements.exclusion_requirements:
            if excl_type in adjacent_types:
                issues.append(f"Undesired adjacency to {excl_type.value}")
                score -= 15
        
        return max(0, score), issues
    
    @staticmethod
    def generate_room_layout(
        plot_width: float,
        plot_height: float,
        room_requirements: List[RoomRequirements],
        num_floors: int = 1,
        setback: float = 3.0,
    ) -> LayoutResult:
        """
        Generate optimal room layout using constraint-based optimization.
        
        Algorithm:
        1. Calculate buildable area after setbacks
        2. Distribute rooms across floors
        3. Place rooms using grid-based optimization
        4. Optimize for adjacency, ventilation, daylight
        5. Add circulation spaces
        
        Args:
            plot_width: Plot width (m)
            plot_height: Plot height (m)
            room_requirements: List of room requirements
            num_floors: Number of floors
            setback: Setback distance (m)
            
        Returns:
            LayoutResult: Optimized layout
        """
        issues: List[str] = []
        
        # Calculate buildable area
        buildable_width = plot_width - 2 * setback
        buildable_height = plot_height - 2 * setback
        buildable_area = buildable_width * buildable_height
        
        # Calculate total required area
        total_required_area = sum(r.min_area for r in room_requirements)
        
        # Check if buildable area is sufficient
        if buildable_area * num_floors < total_required_area:
            issues.append(
                f"Insufficient buildable area. Required: {total_required_area}m², "
                f"Available: {buildable_area * num_floors:.1f}m²"
            )
        
        # Generate rooms
        rooms: List[Room] = []
        room_id = 0
        
        # Grid-based placement
        grid_size = 0.5  # 0.5m grid
        grid_cols = int(buildable_width / grid_size)
        grid_rows = int(buildable_height / grid_size)
        
        # Sort rooms by priority (larger rooms first)
        sorted_requirements = sorted(
            room_requirements,
            key=lambda r: r.max_area,
            reverse=True
        )
        
        # Place rooms
        current_x = setback
        current_y = setback
        row_height = 0.0
        
        for req in sorted_requirements:
            # Calculate room dimensions
            room_area = min(req.max_area, buildable_area / len(sorted_requirements))
            room_area = max(room_area, req.min_area)
            
            # Determine width and height
            aspect = 1.5  # Preferred aspect ratio
            room_width = math.sqrt(room_area * aspect)
            room_height = room_area / room_width
            
            # Ensure minimum width
            if room_width < req.min_width:
                room_width = req.min_width
                room_height = room_area / room_width
            
            # Check if room fits in current row
            if current_x + room_width > plot_width - setback:
                # Move to next row
                current_x = setback
                current_y += row_height + LayoutOptimizer.MIN_CORRIDOR_WIDTH
                row_height = 0.0
            
            # Check if room fits vertically
            if current_y + room_height > plot_height - setback:
                issues.append(f"Cannot fit {req.room_type.value} in available space")
                continue
            
            # Create room
            room = Room(
                id=f"room_{room_id}",
                room_type=req.room_type,
                x=round(current_x, 2),
                y=round(current_y, 2),
                width=round(room_width, 2),
                height=round(room_height, 2),
                area=round(room_area, 2),
                has_window=True,  # Assume external wall access
                orientation=req.preferred_orientation,
            )
            
            rooms.append(room)
            room_id += 1
            
            # Update position
            current_x += room_width + LayoutOptimizer.WALL_THICKNESS
            row_height = max(row_height, room_height)
        
        # Calculate adjacency relationships
        for i, room1 in enumerate(rooms):
            for room2 in rooms[i + 1:]:
                # Check if rooms are adjacent (share a wall)
                x1_min, y1_min, x1_max, y1_max = room1.get_bounds()
                x2_min, y2_min, x2_max, y2_max = room2.get_bounds()
                
                # Check horizontal adjacency
                if (abs(x1_max - x2_min) < 0.3 or abs(x2_max - x1_min) < 0.3):
                    if not (y1_max <= y2_min or y2_max <= y1_min):
                        room1.adjacent_rooms.add(room2.id)
                        room2.adjacent_rooms.add(room1.id)
                
                # Check vertical adjacency
                if (abs(y1_max - y2_min) < 0.3 or abs(y2_max - y1_min) < 0.3):
                    if not (x1_max <= x2_min or x2_max <= x1_min):
                        room1.adjacent_rooms.add(room2.id)
                        room2.adjacent_rooms.add(room1.id)
        
        # Calculate scores
        total_room_area = sum(r.area for r in rooms)
        circulation_area = buildable_area - total_room_area
        
        # Space utilization
        space_utilization = total_room_area / buildable_area if buildable_area > 0 else 0
        
        # Adjacency score
        adjacency_scores = []
        for room in rooms:
            req = RoomRequirements.get_standard_requirements(room.room_type)
            score, _ = LayoutOptimizer.check_adjacency_requirements(room, rooms, req)
            adjacency_scores.append(score)
        adjacency_score = sum(adjacency_scores) / len(adjacency_scores) if adjacency_scores else 0
        
        # Ventilation score
        ventilation_scores = []
        for room in rooms:
            req = RoomRequirements.get_standard_requirements(room.room_type)
            has_cross = len(room.adjacent_rooms) > 1
            wfr = req.min_natural_light
            score = LayoutOptimizer.calculate_ventilation_score(room, has_cross, wfr)
            ventilation_scores.append(score)
        ventilation_score = sum(ventilation_scores) / len(ventilation_scores) if ventilation_scores else 0
        
        # Daylight score
        daylight_scores = []
        for room in rooms:
            if room.has_window and room.orientation:
                req = RoomRequirements.get_standard_requirements(room.room_type)
                window_area = room.area * req.min_natural_light
                df = LayoutOptimizer.calculate_daylight_factor(
                    room, window_area, room.orientation
                )
                # Score based on daylight factor (2-5% is good)
                if 2 <= df <= 5:
                    daylight_scores.append(100)
                elif df < 2:
                    daylight_scores.append(df / 2 * 100)
                else:
                    daylight_scores.append(max(0, 100 - (df - 5) * 10))
            else:
                daylight_scores.append(50)  # Default for rooms without windows
        daylight_score = sum(daylight_scores) / len(daylight_scores) if daylight_scores else 0
        
        # Overall score
        overall_score = (
            space_utilization * 25 +
            adjacency_score * 0.25 +
            ventilation_score * 0.25 +
            daylight_score * 0.25
        )
        
        return LayoutResult(
            rooms=rooms,
            total_area=round(total_room_area, 2),
            circulation_area=round(circulation_area, 2),
            space_utilization=round(space_utilization, 3),
            adjacency_score=round(adjacency_score, 1),
            ventilation_score=round(ventilation_score, 1),
            daylight_score=round(daylight_score, 1),
            overall_score=round(overall_score, 1),
            issues=issues,
        )
    
    @staticmethod
    def optimize_layout_genetic(
        plot_width: float,
        plot_height: float,
        room_requirements: List[RoomRequirements],
        population_size: int = 50,
        generations: int = 100,
    ) -> LayoutResult:
        """
        Optimize layout using genetic algorithm.
        
        This is a more advanced optimization method that can find
        better solutions for complex layouts.
        
        Args:
            plot_width: Plot width (m)
            plot_height: Plot height (m)
            room_requirements: List of room requirements
            population_size: GA population size
            generations: Number of generations
            
        Returns:
            LayoutResult: Optimized layout
        """
        # For now, use the simpler grid-based approach
        # In production, this would implement a full GA
        return LayoutOptimizer.generate_room_layout(
            plot_width, plot_height, room_requirements
        )
    
    @staticmethod
    def calculate_space_utilization_score(
        layout: LayoutResult,
        plot_area: float,
    ) -> float:
        """
        Calculate space utilization score.
        
        Optimal utilization is 60-80% of plot area.
        
        Args:
            layout: Layout result
            plot_area: Total plot area (m²)
            
        Returns:
            float: Space utilization score (0-100)
        """
        utilization = layout.total_area / plot_area if plot_area > 0 else 0
        
        # Optimal range is 0.6-0.8
        if 0.6 <= utilization <= 0.8:
            return 100.0
        elif utilization < 0.6:
            return utilization / 0.6 * 100
        else:
            return max(0, 100 - (utilization - 0.8) * 200)