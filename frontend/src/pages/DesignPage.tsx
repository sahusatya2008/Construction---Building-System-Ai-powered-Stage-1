/**
 * Design Page
 * ===========
 * Main design interface with drawing tools and 3D viewer.
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore, useDesignStore, useDrawingStore, useUIStore } from '../store';
import { api } from '../services/api';
import { PlotDrawing } from '../components/drawing/PlotDrawing';
import { BuildingViewer } from '../components/viewer/BuildingViewer';
import type { 
  Point, 
  SoilType, 
  BuildingType, 
  DesignGenerateRequest
} from '../types';

const SOIL_TYPES: { value: SoilType; label: string }[] = [
  { value: 'clay', label: 'Clay' },
  { value: 'sand', label: 'Sand' },
  { value: 'gravel', label: 'Gravel' },
  { value: 'silt', label: 'Silt' },
  { value: 'rocky', label: 'Rocky' },
  { value: 'loam', label: 'Loam' },
  { value: 'mixed', label: 'Mixed' },
];

const BUILDING_TYPES: { value: BuildingType; label: string }[] = [
  { value: 'residential_single', label: 'Single Family Residential' },
  { value: 'residential_multi', label: 'Multi-Family Residential' },
  { value: 'commercial', label: 'Commercial' },
  { value: 'industrial', label: 'Industrial' },
];

const DesignPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { currentDesign, isGenerating, error, setCurrentDesign, setGenerating, setError } = useDesignStore();
  const points = useDrawingStore((state) => state.points);
  const isClosed = useDrawingStore((state) => state.isClosed);
  
  // Calculate area using Shoelace theorem
  const calculateArea = (pts: Point[]): number => {
    if (pts.length < 3) return 0;
    let area = 0;
    for (let i = 0; i < pts.length; i++) {
      const j = (i + 1) % pts.length;
      area += pts[i].x * pts[j].y;
      area -= pts[j].x * pts[i].y;
    }
    return Math.abs(area / 2);
  };
  
  const plotArea = points.length >= 3 ? calculateArea([...points, points[0]]) : 0;
  const { activePanel, setActivePanel, sidebarOpen, toggleSidebar } = useUIStore();
  
  // Form state
  const [soilType, setSoilType] = useState<SoilType>('sand');
  const [buildingType, setBuildingType] = useState<BuildingType>('residential_single');
  const [numBedrooms, setNumBedrooms] = useState(3);
  const [numBathrooms, setNumBathrooms] = useState(2);
  const [numFloors, setNumFloors] = useState(1);
  const [latitude, setLatitude] = useState(28.6);
  
  const handlePlotComplete = useCallback((pts: Point[]) => {
    console.log('Plot completed with points:', pts);
  }, []);
  
  const handleGenerateDesign = async () => {
    if (points.length < 3 || !isClosed) {
      setError('Please complete the plot boundary first');
      return;
    }
    
    setGenerating(true);
    setError(null);
    
    try {
      const request: DesignGenerateRequest = {
        plot: {
          coordinates: points,
        },
        soil: {
          soil_type: soilType,
        },
        requirements: {
          building_type: buildingType,
          num_bedrooms: numBedrooms,
          num_bathrooms: numBathrooms,
          num_floors: numFloors,
        },
        latitude: latitude,
      };
      
      const design = await api.generateDesign(request);
      setCurrentDesign(design);
      setActivePanel('design');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate design');
    } finally {
      setGenerating(false);
    }
  };
  
  const handleExport = async (format: 'svg' | 'gltf' | 'pdf' | 'json') => {
    if (!currentDesign) return;
    
    try {
      const result = await api.exportDesign(currentDesign.design_id, format);
      // In production, this would trigger a download
      console.log('Export result:', result);
      alert(`Export initiated. Download URL: ${result.download_url}`);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm z-10">
        <div className="px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleSidebar}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-xl font-bold text-indigo-600">ArchAI</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 text-sm">{user?.email}</span>
            <button onClick={handleLogout} className="text-gray-500 hover:text-gray-700">
              Logout
            </button>
          </div>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-80 bg-white shadow-lg overflow-y-auto">
            {/* Panel Tabs */}
            <div className="flex border-b">
              {(['input', 'design', 'export'] as const).map((panel) => (
                <button
                  key={panel}
                  onClick={() => setActivePanel(panel)}
                  className={`flex-1 py-3 text-sm font-medium ${
                    activePanel === panel
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {panel.charAt(0).toUpperCase() + panel.slice(1)}
                </button>
              ))}
            </div>
            
            <div className="p-4">
              {/* Input Panel */}
              {activePanel === 'input' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Plot Information</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      Draw your plot boundary on the canvas
                    </p>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-sm">
                        <span className="text-gray-500">Vertices:</span>{' '}
                        <span className="font-medium">{points.length}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">Status:</span>{' '}
                        <span className={`font-medium ${isClosed ? 'text-green-600' : 'text-amber-600'}`}>
                          {isClosed ? 'Closed' : 'Open'}
                        </span>
                      </div>
                      {points.length >= 3 && (
                        <>
                          <div className="border-t border-gray-200 mt-2 pt-2">
                            <div className="text-lg font-bold text-indigo-600">
                              {plotArea.toFixed(1)} m²
                            </div>
                            <div className="text-xs text-gray-400">
                              {(plotArea * 10.764).toFixed(1)} sq ft
                            </div>
                          </div>
                          {isClosed && (
                            <div className="mt-2 text-xs text-green-600 font-medium flex items-center gap-1">
                              <span>✓</span> Ready for design generation
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Soil Type</h3>
                    <select
                      value={soilType}
                      onChange={(e) => setSoilType(e.target.value as SoilType)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      {SOIL_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Building Type</h3>
                    <select
                      value={buildingType}
                      onChange={(e) => setBuildingType(e.target.value as BuildingType)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      {BUILDING_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Requirements</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm text-gray-600">Bedrooms</label>
                        <input
                          type="number"
                          min="0"
                          max="10"
                          value={numBedrooms}
                          onChange={(e) => setNumBedrooms(parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Bathrooms</label>
                        <input
                          type="number"
                          min="0"
                          max="10"
                          value={numBathrooms}
                          onChange={(e) => setNumBathrooms(parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Floors</label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={numFloors}
                          onChange={(e) => setNumFloors(parseInt(e.target.value) || 1)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Latitude</label>
                        <input
                          type="number"
                          step="0.1"
                          value={latitude}
                          onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                  
                  {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                      {error}
                    </div>
                  )}
                  
                  <button
                    onClick={handleGenerateDesign}
                    disabled={isGenerating || !isClosed}
                    className="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isGenerating ? 'Generating...' : 'Generate Design'}
                  </button>
                </div>
              )}
              
              {/* Design Panel */}
              {activePanel === 'design' && currentDesign && (
                <div className="space-y-6">
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Design Scores</h3>
                    <div className="space-y-2">
                      {Object.entries(currentDesign.scores).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600 capitalize">
                            {key.replace(/_/g, ' ')}
                          </span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-indigo-600 rounded-full"
                                style={{ width: `${value}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium w-12 text-right">
                              {value.toFixed(0)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Foundation</h3>
                    <div className="bg-gray-50 rounded-lg p-3 space-y-1 text-sm">
                      <div><span className="text-gray-500">Type:</span> {currentDesign.foundation.type}</div>
                      <div><span className="text-gray-500">Depth:</span> {currentDesign.foundation.depth}m</div>
                      <div><span className="text-gray-500">Settlement:</span> {currentDesign.foundation.settlement}mm</div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Rooms</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {currentDesign.rooms.map((room) => (
                        <div key={room.id} className="bg-gray-50 rounded-lg p-2 text-sm">
                          <div className="font-medium capitalize">{room.type.replace('_', ' ')}</div>
                          <div className="text-gray-500">{room.area.toFixed(1)} m²</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {currentDesign.warnings.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-800 mb-2">Warnings</h3>
                      <div className="space-y-1">
                        {currentDesign.warnings.map((warning, i) => (
                          <div key={i} className="text-sm text-amber-600">• {warning}</div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {currentDesign.recommendations.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-800 mb-2">Recommendations</h3>
                      <div className="space-y-1">
                        {currentDesign.recommendations.map((rec, i) => (
                          <div key={i} className="text-sm text-blue-600">• {rec}</div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Export Panel */}
              {activePanel === 'export' && (
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-800">Export Design</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => handleExport('svg')}
                      className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg text-left"
                    >
                      <div className="font-medium">2D Blueprint (SVG)</div>
                      <div className="text-sm text-gray-500">Vector format for CAD</div>
                    </button>
                    <button
                      onClick={() => handleExport('gltf')}
                      className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg text-left"
                    >
                      <div className="font-medium">3D Model (GLTF)</div>
                      <div className="text-sm text-gray-500">3D visualization format</div>
                    </button>
                    <button
                      onClick={() => handleExport('pdf')}
                      className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg text-left"
                    >
                      <div className="font-medium">Structural Report (PDF)</div>
                      <div className="text-sm text-gray-500">Detailed analysis report</div>
                    </button>
                    <button
                      onClick={() => handleExport('json')}
                      className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg text-left"
                    >
                      <div className="font-medium">Design Data (JSON)</div>
                      <div className="text-sm text-gray-500">Raw design data</div>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </aside>
        )}
        
        {/* Main Canvas Area */}
        <main className="flex-1 relative">
          {!currentDesign ? (
            <PlotDrawing
              width={800}
              height={600}
              onPlotComplete={handlePlotComplete}
            />
          ) : (
            <BuildingViewer design={currentDesign} />
          )}
        </main>
      </div>
    </div>
  );
};

export default DesignPage;