"""
Design API Endpoints
====================
API routes for architectural design generation and management.
"""

import json
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.domains.geometry.engine import GeometryEngine
from app.domains.soil.engine import SoilAnalysisEngine, SoilProperties, SoilType
from app.domains.optimization.engine import (
    DesignOptimizer,
    DesignConstraints,
    OptimizationWeights,
    BuildingType,
)
from app.models.user import User, Project, Design
from app.schemas.design import (
    DesignGenerateRequest,
    DesignGenerateResponse,
    PlotValidationRequest,
    PlotValidationResponse,
    SoilAnalysisRequest,
    SoilAnalysisResponse,
    RoomSchema,
    FoundationSchema,
    StructuralElementSchema,
    DesignScoresSchema,
    ProjectCreate,
    ProjectResponse,
    ExportRequest,
    ExportResponse,
)

router = APIRouter(prefix="/design", tags=["Design"])


@router.post("/validate-plot", response_model=PlotValidationResponse)
async def validate_plot(
    request: PlotValidationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Validate a plot shape.
    
    Checks:
    - Minimum 3 vertices
    - Non-self-intersecting polygon
    - Area within acceptable range
    - No degenerate edges
    """
    coordinates = request.to_tuples()
    is_valid, error, properties = GeometryEngine.validate_plot_shape(coordinates)
    
    return PlotValidationResponse(
        is_valid=is_valid,
        error=error,
        properties=properties,
    )


@router.post("/analyze-soil", response_model=SoilAnalysisResponse)
async def analyze_soil(
    request: SoilAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Analyze soil and get foundation recommendations.
    
    Returns:
    - Soil bearing capacity
    - Foundation type recommendation
    - Settlement estimate
    - Compatibility score
    """
    try:
        soil_type = SoilType(request.soil_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid soil type: {request.soil_type}"
        )
    
    soil_properties = SoilProperties.get_default_properties(soil_type)
    
    # Get foundation recommendation
    foundation = SoilAnalysisEngine.recommend_foundation_type(
        soil=soil_properties,
        total_load=request.total_load,
        foundation_area=request.foundation_area,
        building_height=request.building_height,
        number_of_stories=request.num_stories,
    )
    
    # Check compatibility
    is_compatible, issues, score = SoilAnalysisEngine.analyze_soil_compatibility(
        soil_properties,
        request.total_load / request.foundation_area,  # Required bearing pressure
    )
    
    return SoilAnalysisResponse(
        soil_type=request.soil_type,
        bearing_capacity=soil_properties.bearing_capacity,
        foundation_recommendation=FoundationSchema(
            type=foundation.foundation_type.value,
            depth=foundation.depth,
            width=foundation.width,
            bearing_pressure=foundation.allowable_bearing_pressure,
            settlement=foundation.settlement_estimate,
            safety_factor=foundation.safety_factor,
            notes=foundation.notes,
        ),
        compatibility_score=score,
        issues=issues,
    )


@router.post("/generate", response_model=DesignGenerateResponse)
async def generate_design(
    request: DesignGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an architectural design.
    
    This is the main endpoint for design generation. It:
    1. Validates the plot geometry
    2. Analyzes soil conditions
    3. Generates room layout
    4. Designs structural elements
    5. Calculates scores
    
    All outputs are deterministic and explainable.
    """
    try:
        # Convert request to domain objects
        coordinates = request.plot.to_tuples()
        
        soil_type = SoilType(request.soil.soil_type.lower())
        building_type = BuildingType(request.requirements.building_type.lower())
        
        constraints = None
        if request.constraints:
            constraints = DesignConstraints(
                max_height=request.constraints.max_height,
                max_floors=request.constraints.max_floors,
                min_setback=request.constraints.min_setback,
                max_coverage=request.constraints.max_coverage,
                min_parking=request.constraints.min_parking,
                min_open_space=request.constraints.min_open_space,
                floor_area_ratio=request.constraints.floor_area_ratio,
            )
        
        weights = None
        if request.optimization_weights:
            weights = OptimizationWeights(
                cost=request.optimization_weights.cost,
                stability=request.optimization_weights.stability,
                ventilation=request.optimization_weights.ventilation,
                daylight=request.optimization_weights.daylight,
                space_utilization=request.optimization_weights.space_utilization,
                aesthetics=request.optimization_weights.aesthetics,
            )
        
        # Generate design
        design = DesignOptimizer.generate_design(
            plot_coordinates=coordinates,
            soil_type=soil_type,
            building_type=building_type,
            num_bedrooms=request.requirements.num_bedrooms,
            num_bathrooms=request.requirements.num_bathrooms,
            num_floors=request.requirements.num_floors,
            constraints=constraints,
            weights=weights,
            latitude=request.latitude,
        )
        
        # Prepare response
        rooms = [
            RoomSchema(
                id=room.id,
                type=room.room_type.value,
                x=room.x,
                y=room.y,
                width=room.width,
                height=room.height,
                area=room.area,
                has_window=room.has_window,
                orientation=room.orientation.value if room.orientation else None,
                adjacent_rooms=list(room.adjacent_rooms),
            )
            for room in design.layout.rooms
        ]
        
        foundation = FoundationSchema(
            type=design.foundation.foundation_type.value,
            depth=design.foundation.depth,
            width=design.foundation.width,
            bearing_pressure=design.foundation.allowable_bearing_pressure,
            settlement=design.foundation.settlement_estimate,
            safety_factor=design.foundation.safety_factor,
            notes=design.foundation.notes,
        )
        
        structural = StructuralElementSchema(
            beams=design.structural_elements.get("beams", []),
            columns=design.structural_elements.get("columns", []),
            slabs=design.structural_elements.get("slabs", []),
        )
        
        scores = DesignScoresSchema(
            safety_score=design.scores.safety_score,
            stability_score=design.scores.stability_score,
            material_efficiency_score=design.scores.material_efficiency_score,
            space_utilization_score=design.scores.space_utilization_score,
            ventilation_score=design.scores.ventilation_score,
            daylight_score=design.scores.daylight_score,
            cost_efficiency_score=design.scores.cost_efficiency_score,
            overall_score=design.scores.overall_score,
        )
        
        # Calculate buildable area
        plot_area = design.plot_geometry.calculate_area()
        buildable_area = design.layout.total_area
        
        return DesignGenerateResponse(
            design_id=design.design_id,
            plot_area=plot_area,
            buildable_area=buildable_area,
            rooms=rooms,
            foundation=foundation,
            structural_elements=structural,
            scores=scores,
            constraints_satisfied=design.constraints_satisfied,
            warnings=design.warnings,
            recommendations=design.recommendations,
            design_data=design.design_data,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Design generation failed: {str(e)}"
        )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    project = Project(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        owner_id=current_user.id,
        status="draft",
        settings=json.dumps(request.settings) if request.settings else None,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status,
        settings=json.loads(project.settings) if project.settings else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's projects."""
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id)
    )
    projects = result.scalars().all()
    
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            owner_id=p.owner_id,
            status=p.status,
            settings=json.loads(p.settings) if p.settings else None,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status,
        settings=json.loads(project.settings) if project.settings else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/export", response_model=ExportResponse)
async def export_design(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Export a design in various formats.
    
    Supported formats:
    - SVG: 2D blueprint
    - GLTF: 3D model
    - PDF: Structural report
    - JSON: Raw design data
    """
    # In production, this would generate actual files
    # For now, return a placeholder response
    
    from datetime import datetime, timedelta
    
    return ExportResponse(
        download_url=f"/api/v1/design/downloads/{request.design_id}.{request.format}",
        format=request.format,
        file_size=1024,  # Placeholder
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )