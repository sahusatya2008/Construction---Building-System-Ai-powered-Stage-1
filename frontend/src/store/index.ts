/**
 * Global State Store
 * ==================
 * Zustand-based state management for the application.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  User,
  DesignGenerateResponse,
  Project,
  Point,
  DrawingState,
  ViewState,
} from '../types';

// ==========================================
// Auth Store
// ==========================================

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user,
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

// ==========================================
// Design Store
// ==========================================

interface DesignState {
  currentDesign: DesignGenerateResponse | null;
  currentProject: Project | null;
  isGenerating: boolean;
  error: string | null;
  
  setCurrentDesign: (design: DesignGenerateResponse | null) => void;
  setCurrentProject: (project: Project | null) => void;
  setGenerating: (generating: boolean) => void;
  setError: (error: string | null) => void;
  clearDesign: () => void;
}

export const useDesignStore = create<DesignState>((set) => ({
  currentDesign: null,
  currentProject: null,
  isGenerating: false,
  error: null,
  
  setCurrentDesign: (currentDesign) => set({ currentDesign, error: null }),
  setCurrentProject: (currentProject) => set({ currentProject }),
  setGenerating: (isGenerating) => set({ isGenerating }),
  setError: (error) => set({ error }),
  clearDesign: () => set({ currentDesign: null, error: null }),
}));

// ==========================================
// Drawing Store
// ==========================================

interface DrawingStore extends DrawingState {
  addPoint: (point: Point) => void;
  updatePoint: (index: number, point: Point) => void;
  removePoint: (index: number) => void;
  setPoints: (points: Point[]) => void;
  setDrawing: (isDrawing: boolean) => void;
  setClosed: (isClosed: boolean) => void;
  selectPoint: (index: number | null) => void;
  clearDrawing: () => void;
  closePolygon: () => void;
}

export const useDrawingStore = create<DrawingStore>()((set, get) => ({
  points: [],
  isDrawing: false,
  isClosed: false,
  selectedPointIndex: null,
  
  addPoint: (point) => set((state) => ({
    points: [...state.points, point],
  })),
  
  updatePoint: (index, point) => set((state) => ({
    points: state.points.map((p, i) => (i === index ? point : p)),
  })),
  
  removePoint: (index) => set((state) => ({
    points: state.points.filter((_, i) => i !== index),
    isClosed: false,
  })),
  
  setPoints: (points) => set({ points, isClosed: false }),
  
  setDrawing: (isDrawing) => set({ isDrawing }),
  
  setClosed: (isClosed) => set({ isClosed }),
  
  selectPoint: (selectedPointIndex) => set({ selectedPointIndex }),
  
  clearDrawing: () => set({
    points: [],
    isDrawing: false,
    isClosed: false,
    selectedPointIndex: null,
  }),
  
  closePolygon: () => {
    const { points } = get();
    if (points.length >= 3) {
      set({ isClosed: true, isDrawing: false });
    }
  },
}));

// ==========================================
// View Store
// ==========================================

interface ViewStore extends ViewState {
  setZoom: (zoom: number) => void;
  setPan: (pan: Point) => void;
  toggleGrid: () => void;
  toggleMeasurements: () => void;
  resetView: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
}

const DEFAULT_VIEW_STATE: ViewState = {
  zoom: 1,
  pan: { x: 0, y: 0 },
  showGrid: true,
  showMeasurements: true,
};

export const useViewStore = create<ViewStore>((set) => ({
  ...DEFAULT_VIEW_STATE,
  
  setZoom: (zoom) => set({ zoom: Math.max(0.1, Math.min(10, zoom)) }),
  
  setPan: (pan) => set({ pan }),
  
  toggleGrid: () => set((state) => ({ showGrid: !state.showGrid })),
  
  toggleMeasurements: () => set((state) => ({ 
    showMeasurements: !state.showMeasurements 
  })),
  
  resetView: () => set(DEFAULT_VIEW_STATE),
  
  zoomIn: () => set((state) => ({ 
    zoom: Math.min(10, state.zoom * 1.2) 
  })),
  
  zoomOut: () => set((state) => ({ 
    zoom: Math.max(0.1, state.zoom / 1.2) 
  })),
}));

// ==========================================
// UI Store
// ==========================================

interface UIState {
  sidebarOpen: boolean;
  activePanel: 'input' | 'design' | 'analysis' | 'export';
  modalOpen: string | null;
  
  toggleSidebar: () => void;
  setActivePanel: (panel: UIState['activePanel']) => void;
  openModal: (modal: string) => void;
  closeModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  activePanel: 'input',
  modalOpen: null,
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setActivePanel: (activePanel) => set({ activePanel }),
  
  openModal: (modalOpen) => set({ modalOpen }),
  
  closeModal: () => set({ modalOpen: null }),
}));