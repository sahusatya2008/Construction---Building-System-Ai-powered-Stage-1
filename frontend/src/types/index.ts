/**
 * TypeScript Type Definitions
 * ===========================
 * Strict typing for all frontend data structures.
 */

// ============================================
// Authentication Types
// ============================================

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'architect' | 'engineer' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ============================================
// Geometry Types
// ============================================

export interface Point {
  x: number;
  y: number;
}

export interface PlotProperties {
  area: number;
  perimeter: number;
  centroid: Point;
  bounding_box: {
    min: Point;
    max: Point;
  };
  dimensions: {
    width: number;
    height: number;
  };
  is_convex: boolean;
  vertex_count: number;
}

export interface PlotValidationResponse {
  is_valid: boolean;
  error: string | null;
  properties: PlotProperties | null;
}

// ============================================
// Soil Types
// ============================================

export type SoilType = 
  | 'clay' 
  | 'sand' 
  | 'gravel' 
  | 'silt' 
  | 'rocky' 
  | 'loam' 
  | 'peat' 
  | 'mixed';

export type FoundationType = 
  | 'shallow_isolated'
  | 'shallow_strip'
  | 'shallow_raft'
  | 'deep_pile'
  | 'deep_pier'
  | 'mat'
  | 'combined';

export interface Foundation {
  type: FoundationType;
  depth: number;
  width: number;
  bearing_pressure: number;
  settlement: number;
  safety_factor: number;
  notes: string[];
}

export interface SoilAnalysisResponse {
  soil_type: SoilType;
  bearing_capacity: number;
  foundation_recommendation: Foundation;
  compatibility_score: number;
  issues: string[];
}

// ============================================
// Layout Types
// ============================================

export type RoomType = 
  | 'living_room'
  | 'bedroom'
  | 'kitchen'
  | 'bathroom'
  | 'dining'
  | 'study'
  | 'garage'
  | 'storage'
  | 'utility'
  | 'entrance'
  | 'corridor'
  | 'balcony';

export type Orientation = 
  | 'north' 
  | 'south' 
  | 'east' 
  | 'west'
  | 'northeast'
  | 'northwest'
  | 'southeast'
  | 'southwest';

export interface Room {
  id: string;
  type: RoomType;
  x: number;
  y: number;
  width: number;
  height: number;
  area: number;
  has_window: boolean;
  orientation: Orientation | null;
  adjacent_rooms: string[];
}

// ============================================
// Structural Types
// ============================================

export interface Beam {
  id: string;
  span: number;
  width: number;
  height: number;
  location: string;
}

export interface Column {
  id: string;
  size: number;
  type: string;
}

export interface Slab {
  id: string;
  thickness: number;
  area: number;
  type: string;
}

export interface StructuralElements {
  beams: Beam[];
  columns: Column[];
  slabs: Slab[];
}

// ============================================
// Design Types
// ============================================

export interface DesignScores {
  safety_score: number;
  stability_score: number;
  material_efficiency_score: number;
  space_utilization_score: number;
  ventilation_score: number;
  daylight_score: number;
  cost_efficiency_score: number;
  overall_score: number;
}

export interface DesignConstraints {
  max_height: number;
  max_floors: number;
  min_setback: number;
  max_coverage: number;
  min_parking: number;
  min_open_space: number;
  floor_area_ratio: number;
}

export interface OptimizationWeights {
  cost: number;
  stability: number;
  ventilation: number;
  daylight: number;
  space_utilization: number;
  aesthetics: number;
}

export type BuildingType = 
  | 'residential_single'
  | 'residential_multi'
  | 'commercial'
  | 'industrial'
  | 'mixed_use';

export interface BuildingRequirements {
  building_type: BuildingType;
  num_bedrooms: number;
  num_bathrooms: number;
  num_floors: number;
}

export interface DesignGenerateRequest {
  plot: {
    coordinates: Point[];
    length?: number;
    width?: number;
    area?: number;
  };
  soil: {
    soil_type: SoilType;
    custom_bearing_capacity?: number;
  };
  requirements: BuildingRequirements;
  constraints?: DesignConstraints;
  optimization_weights?: OptimizationWeights;
  latitude: number;
}

export interface DesignGenerateResponse {
  design_id: string;
  plot_area: number;
  buildable_area: number;
  rooms: Room[];
  foundation: Foundation;
  structural_elements: StructuralElements;
  scores: DesignScores;
  constraints_satisfied: boolean;
  warnings: string[];
  recommendations: string[];
  design_data: Record<string, unknown>;
}

// ============================================
// Project Types
// ============================================

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  settings: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  settings?: Record<string, unknown>;
}

// ============================================
// UI State Types
// ============================================

export interface DrawingState {
  points: Point[];
  isDrawing: boolean;
  isClosed: boolean;
  selectedPointIndex: number | null;
}

export interface ViewState {
  zoom: number;
  pan: Point;
  showGrid: boolean;
  showMeasurements: boolean;
}

export interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  
  // Design
  currentDesign: DesignGenerateResponse | null;
  currentProject: Project | null;
  
  // Drawing
  drawingState: DrawingState;
  
  // View
  viewState: ViewState;
  
  // UI
  isLoading: boolean;
  error: string | null;
}

// ============================================
// API Response Types
// ============================================

export interface ApiError {
  detail: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}