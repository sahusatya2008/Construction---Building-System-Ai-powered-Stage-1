"""
Unit Tests for Geometry Engine
===============================
Tests for polygon calculations and validation.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.domains.geometry.engine import (
    GeometryEngine,
    Point2D,
    Polygon,
)


class TestPoint2D:
    """Tests for Point2D class."""
    
    def test_point_creation(self):
        """Test creating a point."""
        point = Point2D(x=10.0, y=20.0)
        assert point.x == 10.0
        assert point.y == 20.0
    
    def test_point_to_tuple(self):
        """Test converting point to tuple."""
        point = Point2D(x=5.0, y=10.0)
        assert point.to_tuple() == (5.0, 10.0)
    
    def test_distance_to(self):
        """Test distance calculation between points."""
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=3.0, y=4.0)
        
        # Distance should be 5 (3-4-5 triangle)
        assert p1.distance_to(p2) == 5.0


class TestPolygon:
    """Tests for Polygon class."""
    
    def test_polygon_creation(self):
        """Test creating a polygon."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        
        assert len(polygon.vertices) == 4
    
    def test_polygon_minimum_vertices(self):
        """Test that polygon requires at least 3 vertices."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
        ]
        
        with pytest.raises(ValueError):
            Polygon(vertices=vertices)
    
    def test_calculate_area_square(self):
        """Test area calculation for a square."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        
        # Area should be 100 m²
        assert polygon.calculate_area() == 100.0
    
    def test_calculate_area_triangle(self):
        """Test area calculation for a triangle."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=5.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        
        # Area should be 50 m² (base * height / 2)
        assert polygon.calculate_area() == 50.0
    
    def test_calculate_perimeter(self):
        """Test perimeter calculation."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        
        # Perimeter should be 40 m
        assert polygon.calculate_perimeter() == 40.0
    
    def test_calculate_centroid(self):
        """Test centroid calculation."""
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        centroid = polygon.calculate_centroid()
        
        # Centroid should be at (5, 5)
        assert centroid.x == 5.0
        assert centroid.y == 5.0
    
    def test_is_convex(self):
        """Test convexity check."""
        # Square is convex
        vertices = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon = Polygon(vertices=vertices)
        assert polygon.is_convex() == True
        
        # L-shape is concave
        vertices_l = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=10.0, y=0.0),
            Point2D(x=10.0, y=5.0),
            Point2D(x=5.0, y=5.0),
            Point2D(x=5.0, y=10.0),
            Point2D(x=0.0, y=10.0),
        ]
        polygon_l = Polygon(vertices=vertices_l)
        assert polygon_l.is_convex() == False


class TestGeometryEngine:
    """Tests for GeometryEngine class."""
    
    def test_create_polygon_from_coordinates(self):
        """Test creating polygon from coordinate tuples."""
        coordinates = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        polygon = GeometryEngine.create_polygon_from_coordinates(coordinates)
        
        assert len(polygon.vertices) == 4
        assert polygon.calculate_area() == 100.0
    
    def test_validate_plot_shape_valid(self):
        """Test validation of a valid plot shape."""
        coordinates = [(0.0, 0.0), (20.0, 0.0), (20.0, 15.0), (0.0, 15.0)]
        is_valid, error, properties = GeometryEngine.validate_plot_shape(coordinates)
        
        assert is_valid == True
        assert error is None
        assert properties is not None
        assert properties["area"] == 300.0
    
    def test_validate_plot_shape_invalid_self_intersecting(self):
        """Test validation of a self-intersecting polygon."""
        # Bow-tie shape (self-intersecting)
        coordinates = [(0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0)]
        is_valid, error, properties = GeometryEngine.validate_plot_shape(coordinates)
        
        assert is_valid == False
        assert "Invalid polygon" in error
    
    def test_validate_plot_shape_too_few_vertices(self):
        """Test validation with too few vertices."""
        coordinates = [(0.0, 0.0), (10.0, 0.0)]
        is_valid, error, properties = GeometryEngine.validate_plot_shape(coordinates)
        
        assert is_valid == False
        assert "at least 3 vertices" in error.lower()
    
    def test_calculate_setback_polygon(self):
        """Test setback polygon calculation."""
        coordinates = [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)]
        polygon = GeometryEngine.create_polygon_from_coordinates(coordinates)
        
        setback = GeometryEngine.calculate_setback_polygon(polygon, setback_distance=3.0)
        
        assert setback is not None
        # Setback polygon should have smaller area
        assert setback.calculate_area() < polygon.calculate_area()
    
    def test_calculate_compactness(self):
        """Test compactness calculation."""
        # Square has higher compactness
        square_coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        square = GeometryEngine.create_polygon_from_coordinates(square_coords)
        square_compactness = GeometryEngine.calculate_compactness(square)
        
        # Rectangle has lower compactness
        rect_coords = [(0.0, 0.0), (20.0, 0.0), (20.0, 5.0), (0.0, 5.0)]
        rect = GeometryEngine.create_polygon_from_coordinates(rect_coords)
        rect_compactness = GeometryEngine.calculate_compactness(rect)
        
        assert square_compactness > rect_compactness


if __name__ == "__main__":
    pytest.main([__file__, "-v"])