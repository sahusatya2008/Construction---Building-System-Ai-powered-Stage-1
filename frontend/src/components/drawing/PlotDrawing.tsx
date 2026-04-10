/**
 * Plot Drawing Component
 * ======================
 * Interactive polygon drawing tool for plot boundary definition.
 * 
 * Features:
 * - Click to add vertices
 * - Drag to move vertices
 * - Real-time area calculation
 * - Grid snapping
 * - Measurement display
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Stage, Layer, Line, Circle, Text, Group } from 'react-konva';
import { KonvaEventObject } from 'konva/lib/Node';
import { useDrawingStore, useViewStore } from '../../store';
import type { Point } from '../../types';

// Constants
const GRID_SIZE = 10; // meters
const SCALE = 20; // pixels per meter
const VERTEX_RADIUS = 8;
const VERTEX_STROKE_WIDTH = 2;

interface PlotDrawingProps {
  width: number;
  height: number;
  onPlotChange?: (points: Point[]) => void;
  onPlotComplete?: (points: Point[]) => void;
}

export const PlotDrawing: React.FC<PlotDrawingProps> = ({
  width,
  height,
  onPlotChange,
  onPlotComplete,
}) => {
  const stageRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const {
    points,
    isClosed,
    selectedPointIndex,
    addPoint,
    updatePoint,
    removePoint,
    selectPoint,
    closePolygon,
    clearDrawing,
  } = useDrawingStore();
  
  const {
    zoom,
    pan,
    showGrid,
    showMeasurements,
    setZoom,
    setPan,
  } = useViewStore();
  
  const [stageSize, setStageSize] = useState({ width, height });
  
  // Update stage size on container resize
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setStageSize({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };
    
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);
  
  // Convert screen coordinates to world coordinates
  const screenToWorld = useCallback(
    (screenX: number, screenY: number): Point => ({
      x: (screenX - pan.x) / (SCALE * zoom),
      y: (screenY - pan.y) / (SCALE * zoom),
    }),
    [pan, zoom]
  );
  
  // Convert world coordinates to screen coordinates
  const worldToScreen = useCallback(
    (worldX: number, worldY: number): { x: number; y: number } => ({
      x: worldX * SCALE * zoom + pan.x,
      y: worldY * SCALE * zoom + pan.y,
    }),
    [pan, zoom]
  );
  
  // Snap to grid
  const snapToGrid = useCallback(
    (point: Point): Point => {
      if (!showGrid) return point;
      return {
        x: Math.round(point.x / GRID_SIZE) * GRID_SIZE,
        y: Math.round(point.y / GRID_SIZE) * GRID_SIZE,
      };
    },
    [showGrid]
  );
  
  // Handle stage click
  const handleStageClick = useCallback(
    (_e: KonvaEventObject<MouseEvent>) => {
      if (isClosed) return;
      
      const stage = stageRef.current;
      if (!stage) return;
      
      const pos = stage.getPointerPosition();
      if (!pos) return;
      
      const worldPos = screenToWorld(pos.x, pos.y);
      const snappedPos = snapToGrid(worldPos);
      
      // Check if clicking near first point to close polygon
      if (points.length >= 3) {
        const firstPoint = points[0];
        const screenFirst = worldToScreen(firstPoint.x, firstPoint.y);
        const distance = Math.sqrt(
          Math.pow(pos.x - screenFirst.x, 2) + Math.pow(pos.y - screenFirst.y, 2)
        );
        
        if (distance < VERTEX_RADIUS * 2) {
          closePolygon();
          onPlotComplete?.(points);
          return;
        }
      }
      
      addPoint(snappedPos);
      onPlotChange?.([...points, snappedPos]);
    },
    [isClosed, points, addPoint, closePolygon, screenToWorld, worldToScreen, snapToGrid, onPlotChange, onPlotComplete]
  );
  
  // Handle vertex drag
  const handleVertexDrag = useCallback(
    (index: number, e: KonvaEventObject<DragEvent>) => {
      const stage = stageRef.current;
      if (!stage) return;
      
      const pos = e.target.position();
      const worldPos = screenToWorld(pos.x, pos.y);
      const snappedPos = snapToGrid(worldPos);
      
      updatePoint(index, snappedPos);
      onPlotChange?.(points.map((p, i) => (i === index ? snappedPos : p)));
    },
    [points, updatePoint, screenToWorld, snapToGrid, onPlotChange]
  );
  
  // Handle vertex click (for selection/deletion)
  const handleVertexClick = useCallback(
    (index: number, e: KonvaEventObject<MouseEvent>) => {
      e.cancelBubble = true;
      
      if (e.evt.shiftKey && points.length > 3) {
        // Delete vertex on shift+click
        removePoint(index);
        onPlotChange?.(points.filter((_, i) => i !== index));
      } else {
        selectPoint(index);
      }
    },
    [points, removePoint, selectPoint, onPlotChange]
  );
  
  // Handle wheel zoom
  const handleWheel = useCallback(
    (e: KonvaEventObject<WheelEvent>) => {
      e.evt.preventDefault();
      
      const stage = stageRef.current;
      if (!stage) return;
      
      const oldScale = zoom;
      const pointer = stage.getPointerPosition();
      if (!pointer) return;
      
      const scaleBy = 1.1;
      const newScale = e.evt.deltaY < 0 ? oldScale * scaleBy : oldScale / scaleBy;
      
      setZoom(newScale);
      
      // Adjust pan to zoom towards pointer
      const newPan = {
        x: pointer.x - ((pointer.x - pan.x) / oldScale) * newScale,
        y: pointer.y - ((pointer.y - pan.y) / oldScale) * newScale,
      };
      setPan(newPan);
    },
    [zoom, pan, setZoom, setPan]
  );
  
  // Handle pan
  const handleDragEnd = useCallback(
    (e: KonvaEventObject<DragEvent>) => {
      const newPan = {
        x: e.target.x(),
        y: e.target.y(),
      };
      setPan(newPan);
    },
    [setPan]
  );
  
  // Calculate polygon area using Shoelace theorem
  const calculateArea = useCallback((pts: Point[]): number => {
    if (pts.length < 3) return 0;
    
    let area = 0;
    for (let i = 0; i < pts.length; i++) {
      const j = (i + 1) % pts.length;
      area += pts[i].x * pts[j].y;
      area -= pts[j].x * pts[i].y;
    }
    return Math.abs(area / 2);
  }, []);
  
  // Calculate edge length
  const calculateEdgeLength = useCallback((p1: Point, p2: Point): number => {
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  }, []);
  
  // Render grid
  const renderGrid = () => {
    if (!showGrid) return null;
    
    const gridLines: JSX.Element[] = [];
    const gridSpacing = GRID_SIZE * SCALE * zoom;
    
    // Vertical lines
    for (let x = pan.x % gridSpacing; x < stageSize.width; x += gridSpacing) {
      gridLines.push(
        <Line
          key={`v-${x}`}
          points={[x, 0, x, stageSize.height]}
          stroke="#e5e7eb"
          strokeWidth={1}
        />
      );
    }
    
    // Horizontal lines
    for (let y = pan.y % gridSpacing; y < stageSize.height; y += gridSpacing) {
      gridLines.push(
        <Line
          key={`h-${y}`}
          points={[0, y, stageSize.width, y]}
          stroke="#e5e7eb"
          strokeWidth={1}
        />
      );
    }
    
    return gridLines;
  };
  
  // Render measurements
  const renderMeasurements = () => {
    if (!showMeasurements || points.length < 2) return null;
    
    const measurements: JSX.Element[] = [];
    
    // Draw edge measurements
    for (let i = 0; i < points.length; i++) {
      const j = (i + 1) % points.length;
      if (j === 0 && !isClosed) continue;
      
      const p1 = worldToScreen(points[i].x, points[i].y);
      const p2 = worldToScreen(points[j].x, points[j].y);
      
      const length = calculateEdgeLength(points[i], points[j]);
      const midX = (p1.x + p2.x) / 2;
      const midY = (p1.y + p2.y) / 2;
      
      const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);
      
      measurements.push(
        <Group key={`measure-${i}`}>
          <Text
            x={midX}
            y={midY}
            text={`${length.toFixed(1)}m`}
            fontSize={12}
            fill="#374151"
            rotation={(angle * 180) / Math.PI}
            offsetX={20}
            offsetY={6}
          />
        </Group>
      );
    }
    
    return measurements;
  };
  
  // Calculate current area (works even for unclosed polygons)
  const currentArea = points.length >= 3 ? calculateArea([...points, points[0]]) : 0;
  
  // Render polygon
  const renderPolygon = () => {
    if (points.length < 2) return null;
    
    const flatPoints = points.flatMap((p) => {
      const screen = worldToScreen(p.x, p.y);
      return [screen.x, screen.y];
    });
    
    return (
      <Line
        points={flatPoints}
        stroke="#3b82f6"
        strokeWidth={2}
        fill={isClosed ? 'rgba(59, 130, 246, 0.1)' : undefined}
        closed={isClosed}
      />
    );
  };
  
  // Render vertices
  const renderVertices = () => {
    return points.map((point, index) => {
      const screen = worldToScreen(point.x, point.y);
      const isFirst = index === 0;
      const isSelected = index === selectedPointIndex;
      
      return (
        <Circle
          key={`vertex-${index}`}
          x={screen.x}
          y={screen.y}
          radius={VERTEX_RADIUS}
          fill={isFirst && !isClosed ? '#10b981' : isSelected ? '#f59e0b' : '#3b82f6'}
          stroke="#ffffff"
          strokeWidth={VERTEX_STROKE_WIDTH}
          draggable
          onDragMove={(e) => handleVertexDrag(index, e)}
          onClick={(e) => handleVertexClick(index, e)}
          onTap={(e) => handleVertexClick(index, e as unknown as KonvaEventObject<MouseEvent>)}
        />
      );
    });
  };
  
  return (
    <div ref={containerRef} className="relative w-full h-full bg-white">
      <Stage
        ref={stageRef}
        width={stageSize.width}
        height={stageSize.height}
        onClick={handleStageClick}
        onTap={handleStageClick}
        onWheel={handleWheel}
        draggable
        onDragEnd={handleDragEnd}
        x={pan.x}
        y={pan.y}
      >
        <Layer>
          {renderGrid()}
          {renderPolygon()}
          {renderMeasurements()}
          {renderVertices()}
        </Layer>
      </Stage>
      
      {/* Toolbar */}
      <div className="absolute top-4 left-4 flex gap-2">
        <button
          onClick={clearDrawing}
          className="px-3 py-1.5 bg-red-500 text-white rounded-md text-sm hover:bg-red-600 transition-colors"
        >
          Clear
        </button>
        {points.length >= 3 && !isClosed && (
          <button
            onClick={() => {
              closePolygon();
              onPlotComplete?.(points);
            }}
            className="px-3 py-1.5 bg-green-500 text-white rounded-md text-sm hover:bg-green-600 transition-colors"
          >
            Close Polygon
          </button>
        )}
      </div>
      
      {/* Instructions */}
      <div className="absolute bottom-4 left-4 text-sm text-gray-500">
        {isClosed ? (
          <span>Polygon closed. Drag vertices to adjust. Shift+click to delete.</span>
        ) : (
          <span>Click to add vertices. Click first point to close polygon.</span>
        )}
      </div>
      
      {/* Area Display - Prominent */}
      {points.length >= 3 && (
        <div className="absolute top-4 right-4 bg-white shadow-lg rounded-lg p-4 border-2 border-indigo-500">
          <div className="text-sm text-gray-500 mb-1">Plot Area</div>
          <div className="text-2xl font-bold text-indigo-600">
            {currentArea.toFixed(1)} m²
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {(currentArea * 10.764).toFixed(1)} sq ft
          </div>
          {isClosed && (
            <div className="mt-2 text-xs text-green-600 font-medium">
              ✓ Ready for design
            </div>
          )}
        </div>
      )}
      
      {/* Zoom indicator */}
      <div className="absolute bottom-4 right-4 text-sm text-gray-500">
        Zoom: {(zoom * 100).toFixed(0)}%
      </div>
    </div>
  );
};

export default PlotDrawing;