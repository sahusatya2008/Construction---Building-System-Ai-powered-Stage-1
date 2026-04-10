"""
Geometry Engine Module
======================
Core geometric calculations for architectural planning.

Implements:
- Polygon area calculation (Shoelace theorem)
- Centroid calculation
- Polygon validation (non-intersecting, closed)
- Coordinate transformations
- Geometric utilities

All formulas are mathematically precise and documented.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint
from shapely.validation import explain_validity


@dataclass
class Point2D:
    """
    2D Point representation.
    
    Attributes:
        x: X coordinate
        y: Y coordinate
    """
    x: float
    y: float
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple representation."""
        return (self.x, self.y)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.x, self.y])
    
    def distance_to(self, other: "Point2D") -> float:
        """
        Calculate Euclidean distance to another point.
        
        Formula: d = √((x₂-x₁)² + (y₂-y₁)²)
        
        Args:
            other: Another point
            
        Returns:
            float: Euclidean distance
        """
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class Polygon:
    """
    Polygon representation with vertices.
    
    Attributes:
        vertices: List of 2D points forming the polygon
    """
    vertices: List[Point2D]
    
    def __post_init__(self):
        """Validate polygon after initialization."""
        if len(self.vertices) < 3:
            raise ValueError("Polygon must have at least 3 vertices")
    
    def to_shapely(self) -> ShapelyPolygon:
        """Convert to Shapely polygon for advanced operations."""
        coords = [(v.x, v.y) for v in self.vertices]
        return ShapelyPolygon(coords)
    
    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Check if polygon is valid (non-self-intersecting, closed).
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        shapely_poly = self.to_shapely()
        
        if not shapely_poly.is_valid:
            reason = explain_validity(shapely_poly)
            return False, f"Invalid polygon: {reason}"
        
        return True, None
    
    def calculate_area(self) -> float:
        """
        Calculate polygon area using the Shoelace theorem.
        
        Shoelace Theorem:
        A = ½|Σᵢ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)|
        
        where vertices are ordered (x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ)
        and (xₙ₊₁,yₙ₊₁) = (x₁,y₁) to close the polygon.
        
        Returns:
            float: Absolute area in square units
        """
        n = len(self.vertices)
        if n < 3:
            return 0.0
        
        # Apply Shoelace formula
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y
        
        return abs(area) / 2.0
    
    def calculate_perimeter(self) -> float:
        """
        Calculate polygon perimeter.
        
        Formula: P = Σᵢ √((xᵢ₊₁-xᵢ)² + (yᵢ₊₁-yᵢ)²)
        
        Returns:
            float: Perimeter in linear units
        """
        n = len(self.vertices)
        perimeter = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            perimeter += self.vertices[i].distance_to(self.vertices[j])
        
        return perimeter
    
    def calculate_centroid(self) -> Point2D:
        """
        Calculate polygon centroid (center of mass).
        
        Centroid formulas:
        Cx = (1/6A) * Σᵢ(xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
        Cy = (1/6A) * Σᵢ(yᵢ + yᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
        
        where A is the signed area from the Shoelace formula.
        
        Returns:
            Point2D: Centroid coordinates
        """
        n = len(self.vertices)
        if n < 3:
            return Point2D(0.0, 0.0)
        
        # Calculate signed area
        signed_area = 0.0
        for i in range(n):
            j = (i + 1) % n
            signed_area += (
                self.vertices[i].x * self.vertices[j].y
                - self.vertices[j].x * self.vertices[i].y
            )
        signed_area /= 2.0
        
        if abs(signed_area) < 1e-10:
            # Degenerate polygon, return average of vertices
            avg_x = sum(v.x for v in self.vertices) / n
            avg_y = sum(v.y for v in self.vertices) / n
            return Point2D(avg_x, avg_y)
        
        # Calculate centroid
        cx = 0.0
        cy = 0.0
        for i in range(n):
            j = (i + 1) % n
            cross = (
                self.vertices[i].x * self.vertices[j].y
                - self.vertices[j].x * self.vertices[i].y
            )
            cx += (self.vertices[i].x + self.vertices[j].x) * cross
            cy += (self.vertices[i].y + self.vertices[j].y) * cross
        
        cx /= (6.0 * signed_area)
        cy /= (6.0 * signed_area)
        
        return Point2D(cx, cy)
    
    def get_bounding_box(self) -> Tuple[Point2D, Point2D]:
        """
        Calculate axis-aligned bounding box.
        
        Returns:
            Tuple[Point2D, Point2D]: (min_corner, max_corner)
        """
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        
        return (Point2D(min(xs), min(ys)), Point2D(max(xs), max(ys)))
    
    def get_dimensions(self) -> Tuple[float, float]:
        """
        Get polygon dimensions (width and height).
        
        Returns:
            Tuple[float, float]: (width, height)
        """
        min_corner, max_corner = self.get_bounding_box()
        width = max_corner.x - min_corner.x
        height = max_corner.y - min_corner.y
        return (width, height)
    
    def contains_point(self, point: Point2D) -> bool:
        """
        Check if a point is inside the polygon using ray casting.
        
        Args:
            point: Point to check
            
        Returns:
            bool: True if point is inside polygon
        """
        shapely_poly = self.to_shapely()
        return shapely_poly.contains(ShapelyPoint(point.x, point.y))
    
    def is_convex(self) -> bool:
        """
        Check if polygon is convex.
        
        A polygon is convex if all interior angles are less than 180°.
        This is checked by verifying that all cross products have the same sign.
        
        Returns:
            bool: True if polygon is convex
        """
        n = len(self.vertices)
        if n < 3:
            return False
        
        # Calculate cross product sign for first edge pair
        def cross_product_sign(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
            """Calculate Z component of cross product for edge vectors."""
            v1 = (p2.x - p1.x, p2.y - p1.y)
            v2 = (p3.x - p2.x, p3.y - p2.y)
            return v1[0] * v2[1] - v1[1] * v2[0]
        
        # Get initial sign
        initial_sign = cross_product_sign(
            self.vertices[0], self.vertices[1], self.vertices[2]
        )
        
        # Check all consecutive edge pairs
        for i in range(1, n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            p3 = self.vertices[(i + 2) % n]
            
            sign = cross_product_sign(p1, p2, p3)
            
            # If signs differ, polygon is concave
            if initial_sign * sign < 0:
                return False
        
        return True
    
    def simplify(self, tolerance: float = 0.01) -> "Polygon":
        """
        Simplify polygon by removing redundant vertices.
        
        Uses Douglas-Peucker algorithm via Shapely.
        
        Args:
            tolerance: Simplification tolerance
            
        Returns:
            Polygon: Simplified polygon
        """
        shapely_poly = self.to_shapely()
        simplified = shapely_poly.simplify(tolerance)
        
        coords = list(simplified.exterior.coords)[:-1]  # Remove closing point
        vertices = [Point2D(x, y) for x, y in coords]
        
        return Polygon(vertices)


class GeometryEngine:
    """
    Main geometry engine for architectural calculations.
    
    Provides high-level geometric operations for the AI design system.
    """
    
    @staticmethod
    def create_polygon_from_coordinates(
        coordinates: List[Tuple[float, float]]
    ) -> Polygon:
        """
        Create a polygon from a list of coordinate tuples.
        
        Args:
            coordinates: List of (x, y) tuples
            
        Returns:
            Polygon: Created polygon
            
        Raises:
            ValueError: If coordinates are invalid
        """
        if len(coordinates) < 3:
            raise ValueError("At least 3 coordinates required for a polygon")
        
        vertices = [Point2D(x, y) for x, y in coordinates]
        return Polygon(vertices)
    
    @staticmethod
    def validate_plot_shape(
        coordinates: List[Tuple[float, float]],
        min_area: float = 10.0,
        max_area: float = 1000000.0,
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Validate a plot shape for architectural design.
        
        Checks:
        - Minimum 3 vertices
        - Non-self-intersecting
        - Area within acceptable range
        - No degenerate edges
        
        Args:
            coordinates: List of (x, y) coordinate tuples
            min_area: Minimum acceptable area (m²)
            max_area: Maximum acceptable area (m²)
            
        Returns:
            Tuple containing:
            - bool: Is valid
            - Optional[str]: Error message if invalid
            - Optional[dict]: Computed properties if valid
        """
        # Check minimum vertices
        if len(coordinates) < 3:
            return False, "Plot must have at least 3 vertices", None
        
        try:
            polygon = GeometryEngine.create_polygon_from_coordinates(coordinates)
        except Exception as e:
            return False, f"Invalid coordinates: {str(e)}", None
        
        # Check polygon validity
        is_valid, error = polygon.is_valid()
        if not is_valid:
            return False, error, None
        
        # Check area
        area = polygon.calculate_area()
        if area < min_area:
            return False, f"Plot area ({area:.2f} m²) is below minimum ({min_area} m²)", None
        if area > max_area:
            return False, f"Plot area ({area:.2f} m²) exceeds maximum ({max_area} m²)", None
        
        # Check for degenerate edges (edges shorter than 0.1m)
        for i in range(len(polygon.vertices)):
            j = (i + 1) % len(polygon.vertices)
            edge_length = polygon.vertices[i].distance_to(polygon.vertices[j])
            if edge_length < 0.1:
                return False, f"Degenerate edge detected (length: {edge_length:.4f}m)", None
        
        # Compute properties
        centroid = polygon.calculate_centroid()
        bbox_min, bbox_max = polygon.get_bounding_box()
        width, height = polygon.get_dimensions()
        
        properties = {
            "area": area,
            "perimeter": polygon.calculate_perimeter(),
            "centroid": {"x": centroid.x, "y": centroid.y},
            "bounding_box": {
                "min": {"x": bbox_min.x, "y": bbox_min.y},
                "max": {"x": bbox_max.x, "y": bbox_max.y},
            },
            "dimensions": {"width": width, "height": height},
            "is_convex": polygon.is_convex(),
            "vertex_count": len(polygon.vertices),
        }
        
        return True, None, properties
    
    @staticmethod
    def calculate_setback_polygon(
        polygon: Polygon,
        setback_distance: float,
    ) -> Optional[Polygon]:
        """
        Calculate setback polygon (offset inward).
        
        The setback polygon represents the buildable area after
        applying regulatory setbacks from property boundaries.
        
        Args:
            polygon: Original plot polygon
            setback_distance: Setback distance in meters
            
        Returns:
            Optional[Polygon]: Setback polygon or None if invalid
        """
        shapely_poly = polygon.to_shapely()
        
        # Offset inward (negative buffer)
        setback_poly = shapely_poly.buffer(-setback_distance)
        
        if setback_poly.is_empty:
            return None
        
        # Get exterior coordinates
        coords = list(setback_poly.exterior.coords)[:-1]
        vertices = [Point2D(x, y) for x, y in coords]
        
        try:
            return Polygon(vertices)
        except ValueError:
            return None
    
    @staticmethod
    def subdivide_polygon(
        polygon: Polygon,
        num_divisions: int,
        direction: str = "horizontal",
    ) -> List[Polygon]:
        """
        Subdivide polygon into equal strips.
        
        Useful for creating room divisions or floor plates.
        
        Args:
            polygon: Polygon to subdivide
            num_divisions: Number of divisions
            direction: 'horizontal' or 'vertical'
            
        Returns:
            List[Polygon]: List of subdivided polygons
        """
        shapely_poly = polygon.to_shapely()
        min_corner, max_corner = polygon.get_bounding_box()
        
        divisions = []
        
        if direction == "horizontal":
            total_height = max_corner.y - min_corner.y
            strip_height = total_height / num_divisions
            
            for i in range(num_divisions):
                y_min = min_corner.y + i * strip_height
                y_max = min_corner.y + (i + 1) * strip_height
                
                # Create strip polygon
                strip = ShapelyPolygon([
                    (min_corner.x - 1, y_min),
                    (max_corner.x + 1, y_min),
                    (max_corner.x + 1, y_max),
                    (min_corner.x - 1, y_max),
                ])
                
                # Intersect with original polygon
                intersection = shapely_poly.intersection(strip)
                
                if not intersection.is_empty:
                    if intersection.geom_type == "Polygon":
                        coords = list(intersection.exterior.coords)[:-1]
                        vertices = [Point2D(x, y) for x, y in coords]
                        try:
                            divisions.append(Polygon(vertices))
                        except ValueError:
                            pass
        
        else:  # vertical
            total_width = max_corner.x - min_corner.x
            strip_width = total_width / num_divisions
            
            for i in range(num_divisions):
                x_min = min_corner.x + i * strip_width
                x_max = min_corner.x + (i + 1) * strip_width
                
                strip = ShapelyPolygon([
                    (x_min, min_corner.y - 1),
                    (x_max, min_corner.y - 1),
                    (x_max, max_corner.y + 1),
                    (x_min, max_corner.y + 1),
                ])
                
                intersection = shapely_poly.intersection(strip)
                
                if not intersection.is_empty:
                    if intersection.geom_type == "Polygon":
                        coords = list(intersection.exterior.coords)[:-1]
                        vertices = [Point2D(x, y) for x, y in coords]
                        try:
                            divisions.append(Polygon(vertices))
                        except ValueError:
                            pass
        
        return divisions
    
    @staticmethod
    def calculate_aspect_ratio(polygon: Polygon) -> float:
        """
        Calculate aspect ratio of polygon bounding box.
        
        Returns:
            float: Aspect ratio (width/height)
        """
        width, height = polygon.get_dimensions()
        
        if height == 0:
            return float('inf')
        
        return width / height
    
    @staticmethod
    def calculate_compactness(polygon: Polygon) -> float:
        """
        Calculate compactness ratio (isoperimetric quotient).
        
        Formula: Q = 4πA/P²
        
        where A is area and P is perimeter.
        A circle has Q = 1, all other shapes have Q < 1.
        
        Returns:
            float: Compactness ratio (0 to 1)
        """
        area = polygon.calculate_area()
        perimeter = polygon.calculate_perimeter()
        
        if perimeter == 0:
            return 0.0
        
        return (4 * np.pi * area) / (perimeter ** 2)