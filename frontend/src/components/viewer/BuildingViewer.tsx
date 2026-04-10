/**
 * 3D Building Viewer Component
 * =============================
 * Three.js based 3D visualization for generated building designs.
 * 
 * Features:
 * - Room visualization with different colors
 * - Interactive camera controls
 * - Floor navigation
 * - Export to GLTF
 */

import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera,
  Environment,
  Grid,
  Box,
  Plane,
  Html,
} from '@react-three/drei';
import * as THREE from 'three';
import type { Room, DesignGenerateResponse } from '../../types';

// Room colors based on type
const ROOM_COLORS: Record<string, string> = {
  living_room: '#3b82f6',
  bedroom: '#8b5cf6',
  kitchen: '#f59e0b',
  bathroom: '#06b6d4',
  dining: '#10b981',
  study: '#6366f1',
  garage: '#6b7280',
  storage: '#9ca3af',
  utility: '#f97316',
  entrance: '#84cc16',
  corridor: '#d1d5db',
  balcony: '#a3e635',
};

interface BuildingViewerProps {
  design: DesignGenerateResponse | null;
  showLabels?: boolean;
  showGrid?: boolean;
  floor?: number;
}

// Room mesh component
const RoomMesh: React.FC<{
  room: Room;
  height: number;
  showLabel: boolean;
}> = ({ room, height, showLabel }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  const color = ROOM_COLORS[room.type] || '#94a3b8';
  
  // Create room geometry
  const position: [number, number, number] = [
    room.x + room.width / 2,
    height / 2,
    room.y + room.height / 2,
  ];
  
  const scale: [number, number, number] = [
    room.width,
    height,
    room.height,
  ];
  
  return (
    <group position={position}>
      {/* Room box */}
      <Box
        ref={meshRef}
        args={[1, 1, 1]}
        scale={scale}
      >
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.7}
          side={THREE.DoubleSide}
        />
      </Box>
      
      {/* Room edges */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(1, 1, 1)]} />
        <lineBasicMaterial color="#1f2937" />
      </lineSegments>
      
      {/* Room label */}
      {showLabel && (
        <Html
          position={[0, height / 2 + 0.5, 0]}
          center
          style={{
            background: 'rgba(255,255,255,0.9)',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
          }}
        >
          <div>
            <div className="font-medium capitalize">
              {room.type.replace('_', ' ')}
            </div>
            <div className="text-xs text-gray-500">
              {room.area.toFixed(1)} m²
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

// Floor component
const Floor: React.FC<{
  rooms: Room[];
  floorNumber: number;
  showLabels: boolean;
}> = ({ rooms, floorNumber, showLabels }) => {
  const floorHeight = 3; // meters
  const baseY = floorNumber * floorHeight;
  
  return (
    <group position={[0, baseY, 0]}>
      {/* Floor slab */}
      <Plane
        args={[100, 100]}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.1, 0]}
      >
        <meshStandardMaterial color="#e5e7eb" />
      </Plane>
      
      {/* Rooms */}
      {rooms.map((room) => (
        <RoomMesh
          key={room.id}
          room={room}
          height={floorHeight - 0.2}
          showLabel={showLabels}
        />
      ))}
    </group>
  );
};

// Plot boundary visualization
const PlotBoundary: React.FC<{
  coordinates: Array<{ x: number; y: number }>;
}> = ({ coordinates }) => {
  const points = useMemo(() => {
    const pts = coordinates.map((c) => new THREE.Vector3(c.x, 0, c.y));
    pts.push(new THREE.Vector3(coordinates[0].x, 0, coordinates[0].y));
    return pts;
  }, [coordinates]);
  
  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);
  
  return (
    <group>
      <primitive object={new THREE.Line(lineGeometry, new THREE.LineBasicMaterial({ color: '#ef4444', linewidth: 2 }))} />
      {/* Plot corners */}
      {coordinates.map((coord, index) => (
        <mesh key={index} position={[coord.x, 0, coord.y]}>
          <sphereGeometry args={[0.3, 16, 16]} />
          <meshStandardMaterial color="#ef4444" />
        </mesh>
      ))}
    </group>
  );
};

// Main scene component
const Scene: React.FC<BuildingViewerProps> = ({
  design,
  showLabels = true,
  showGrid = true,
  floor = 0,
}) => {
  useThree();
  
  // Calculate scene center
  const center = useMemo(() => {
    if (!design || design.rooms.length === 0) {
      return { x: 0, y: 0, z: 0 };
    }
    
    const sumX = design.rooms.reduce((acc, r) => acc + r.x + r.width / 2, 0);
    const sumZ = design.rooms.reduce((acc, r) => acc + r.y + r.height / 2, 0);
    
    return {
      x: sumX / design.rooms.length,
      y: 0,
      z: sumZ / design.rooms.length,
    };
  }, [design]);
  
  return (
    <>
      {/* Camera */}
      <PerspectiveCamera
        makeDefault
        position={[center.x + 30, 30, center.z + 30]}
        fov={50}
        near={0.1}
        far={1000}
      />
      
      {/* Controls */}
      <OrbitControls
        target={[center.x, 0, center.z]}
        enableDamping
        dampingFactor={0.05}
        minDistance={5}
        maxDistance={200}
        maxPolarAngle={Math.PI / 2 - 0.1}
      />
      
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[50, 50, 25]}
        intensity={1}
        castShadow
        shadow-mapSize={[2048, 2048]}
      />
      <directionalLight position={[-25, 25, -25]} intensity={0.5} />
      
      {/* Environment */}
      <Environment preset="city" />
      
      {/* Grid */}
      {showGrid && (
        <Grid
          args={[200, 200]}
          cellSize={5}
          cellThickness={0.5}
          cellColor="#94a3b8"
          sectionSize={20}
          sectionThickness={1}
          sectionColor="#64748b"
          fadeDistance={100}
          fadeStrength={1}
          followCamera={false}
          infiniteGrid
        />
      )}
      
      {/* Plot boundary */}
      {design?.design_data && (design.design_data as any).plot?.coordinates && (
        <PlotBoundary coordinates={(design.design_data as any).plot.coordinates} />
      )}
      
      {/* Building floors */}
      {design?.rooms && (
        <Floor
          rooms={design.rooms}
          floorNumber={floor}
          showLabels={showLabels}
        />
      )}
      
      {/* Axis helper */}
      <axesHelper args={[20]} />
    </>
  );
};

// Loading fallback
const LoadingFallback: React.FC = () => (
  <Html center>
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <span>Loading 3D model...</span>
    </div>
  </Html>
);

// Main viewer component
export const BuildingViewer: React.FC<BuildingViewerProps> = (props) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  return (
    <div ref={containerRef} className="w-full h-full bg-gray-100">
      <Canvas shadows>
        <Suspense fallback={<LoadingFallback />}>
          <Scene {...props} />
        </Suspense>
      </Canvas>
      
      {/* Controls overlay */}
      <div className="absolute bottom-4 left-4 flex gap-2">
        <div className="px-3 py-1.5 bg-white rounded-md shadow text-sm">
          Drag to rotate | Scroll to zoom | Shift+drag to pan
        </div>
      </div>
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white rounded-md shadow p-3">
        <div className="text-sm font-medium mb-2">Room Types</div>
        <div className="grid grid-cols-2 gap-1 text-xs">
          {Object.entries(ROOM_COLORS).slice(0, 8).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1">
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: color }}
              />
              <span className="capitalize">{type.replace('_', ' ')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BuildingViewer;