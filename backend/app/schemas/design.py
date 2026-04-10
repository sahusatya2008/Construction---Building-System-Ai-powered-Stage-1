"""
Design Schemas
==============
Pydantic schemas for design-related API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PointSchema(BaseModel):
    """2D Point schema."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class PlotInputSchema(BaseModel):
    """Input schema for plot definition."""
    coordinates: List[PointSchema] = Field(
        ...,
        min_length=3,
        description="List of coordinates defining the plot boundary"
    )
    length: Optional[float] = Field(None, gt=0, description="Plot length (m)")
    width: Optional[float] = Field(None, gt=0, description="Plot width (m)")
    area: Optional[float] = Field(None, gt=0, description="Plot area (m²)")
    
    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) < 3:
            raise ValueError("At least 3 coordinates required for a polygon")
        return v
    
    def to_tuples(self) -> List[tuple]:
        """Convert to list of tuples."""
        return [(p.x, p.y) for p in self.coordinates]


class SoilInputSchema(BaseModel):
    """Input schema for soil parameters."""
    soil_type: str = Field(
        ...,
        description="Type of soil (clay, sand, gravel, silt, rocky, loam, peat, mixed)"
    )
    custom_bearing_capacity: Optional[float] = Field(
        None,
        gt=0,
        description="Custom bearing capacity (kN/m²) if known"
    )
    
    @field_validator('soil_type')
    @classmethod
    def validate_soil_type(cls, v):
        valid_types = ['clay', 'sand', 'gravel', 'silt', 'rocky', 'loam', 'peat', 'mixed']
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid soil type. Must be one of: {valid_types}")
        return v.lower()


class ConstraintsSchema(BaseModel):
    """Design constraints schema."""
    max_height: float = Field(15.0, gt=0, description="Maximum building height (m)")
    max_floors: int = Field(4, ge=1, le=50, description="Maximum number of floors")
    min_setback: float = Field(3.0, ge=0, description="Minimum setback (m)")
    max_coverage: float = Field(0.6, gt=0, le=1, description="Maximum plot coverage")
    min_parking: int = Field(1, ge=0, description="Minimum parking spaces")
    min_open_space: float = Field(0.2, ge=0, le=1, description="Minimum open space ratio")
    floor_area_ratio: float = Field(2.0, gt=0, description="Maximum FAR")


class OptimizationWeightsSchema(BaseModel):
    """Optimization weights schema."""
    cost: float = Field(0.15, ge=0, le=1)
    stability: float = Field(0.25, ge=0, le=1)
    ventilation: float = Field(0.15, ge=0, le=1)
    daylight: float = Field(0.15, ge=0, le=1)
    space_utilization: float = Field(0.15, ge=0, le=1)
    aesthetics: float = Field(0.15, ge=0, le=1)


class BuildingRequirementsSchema(BaseModel):
    """Building requirements schema."""
    building_type: str = Field(
        "residential_single",
        description="Type of building"
    )
    num_bedrooms: int = Field(2, ge=0, description="Number of bedrooms")
    num_bathrooms: int = Field(1, ge=0, description="Number of bathrooms")
    num_floors: int = Field(1, ge=1, le=10, description="Number of floors")
    
    @field_validator('building_type')
    @classmethod
    def validate_building_type(cls, v):
        valid_types = [
            'residential_single', 'residential_multi',
            'commercial', 'industrial', 'mixed_use'
        ]
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid building type. Must be one of: {valid_types}")
        return v.lower()


class DesignGenerateRequest(BaseModel):
    """Request schema for design generation."""
    plot: PlotInputSchema
    soil: SoilInputSchema
    requirements: BuildingRequirementsSchema
    constraints: Optional[ConstraintsSchema] = None
    optimization_weights: Optional[OptimizationWeightsSchema] = None
    latitude: float = Field(28.0, ge=-90, le=90, description="Site latitude")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plot": {
                    "coordinates": [
                        {"x": 0, "y": 0},
                        {"x": 20, "y": 0},
                        {"x": 20, "y": 15},
                        {"x": 0, "y": 15}
                    ]
                },
                "soil": {
                    "soil_type": "sand"
                },
                "requirements": {
                    "building_type": "residential_single",
                    "num_bedrooms": 3,
                    "num_bathrooms": 2,
                    "num_floors": 2
                },
                "constraints": {
                    "max_height": 10,
                    "max_floors": 2,
                    "min_setback": 3
                },
                "latitude": 28.6
            }
        }


class RoomSchema(BaseModel):
    """Room output schema."""
    id: str
    type: str
    x: float
    y: float
    width: float
    height: float
    area: float
    has_window: bool
    orientation: Optional[str] = None
    adjacent_rooms: List[str] = []


class FoundationSchema(BaseModel):
    """Foundation output schema."""
    type: str
    depth: float
    width: float
    bearing_pressure: float
    settlement: float
    safety_factor: float
    notes: List[str] = []


class StructuralElementSchema(BaseModel):
    """Structural element schema."""
    beams: List[Dict[str, Any]] = []
    columns: List[Dict[str, Any]] = []
    slabs: List[Dict[str, Any]] = []


class DesignScoresSchema(BaseModel):
    """Design scores schema."""
    safety_score: float
    stability_score: float
    material_efficiency_score: float
    space_utilization_score: float
    ventilation_score: float
    daylight_score: float
    cost_efficiency_score: float
    overall_score: float


class DesignGenerateResponse(BaseModel):
    """Response schema for design generation."""
    design_id: str
    plot_area: float
    buildable_area: float
    rooms: List[RoomSchema]
    foundation: FoundationSchema
    structural_elements: StructuralElementSchema
    scores: DesignScoresSchema
    constraints_satisfied: bool
    warnings: List[str] = []
    recommendations: List[str] = []
    design_data: Dict[str, Any]


class PlotValidationRequest(BaseModel):
    """Request schema for plot validation."""
    coordinates: List[PointSchema]
    
    def to_tuples(self) -> List[tuple]:
        return [(p.x, p.y) for p in self.coordinates]


class PlotValidationResponse(BaseModel):
    """Response schema for plot validation."""
    is_valid: bool
    error: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class SoilAnalysisRequest(BaseModel):
    """Request schema for soil analysis."""
    soil_type: str
    total_load: float = Field(..., gt=0, description="Total structural load (kN)")
    foundation_area: float = Field(..., gt=0, description="Foundation area (m²)")
    building_height: float = Field(..., gt=0, description="Building height (m)")
    num_stories: int = Field(..., ge=1, description="Number of stories")


class SoilAnalysisResponse(BaseModel):
    """Response schema for soil analysis."""
    soil_type: str
    bearing_capacity: float
    foundation_recommendation: FoundationSchema
    compatibility_score: float
    issues: List[str] = []


class ExportRequest(BaseModel):
    """Request schema for design export."""
    design_id: str
    format: str = Field(..., pattern="^(svg|gltf|pdf|json)$")
    include_structural_report: bool = True
    include_load_report: bool = True
    include_material_report: bool = True


class ExportResponse(BaseModel):
    """Response schema for design export."""
    download_url: str
    format: str
    file_size: int
    expires_at: datetime


# Project Schemas
class ProjectCreate(BaseModel):
    """Schema for creating a project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    status: str
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DesignListResponse(BaseModel):
    """Schema for design list item."""
    id: str
    name: str
    status: str
    overall_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True