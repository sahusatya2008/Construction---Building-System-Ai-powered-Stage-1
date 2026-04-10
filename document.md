# ArchAI Platform — Technical Documentation

**AI-Powered Architectural Planning System**

---

## 📋 Document Information

| Field | Details |
|-------|---------|
| **Project Name** | ArchAI Platform |
| **Version** | 1.0.0 |
| **Developer** | Satya Narayan Sahu |
| **Designing & Planning** | Tathoi Mondal |
| **Technology Stack** | Python 3.12, FastAPI, React 18, TypeScript, PostgreSQL, Redis, Docker |
| **Document Type** | System Technical Documentation |
| **Last Updated** | January 2026 |

---

## 📖 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Project Structure & Directory Layout](#3-project-structure--directory-layout)
4. [Backend Architecture Deep Dive](#4-backend-architecture-deep-dive)
5. [Frontend Architecture Deep Dive](#5-frontend-architecture-deep-dive)
6. [Geometry Engine — Algorithms & Mathematics](#6-geometry-engine--algorithms--mathematics)
7. [Soil Analysis Engine — Geotechnical Engineering](#7-soil-analysis-engine--geotechnical-engineering)
8. [Structural Solver — Engineering Calculations](#8-structural-solver--engineering-calculations)
9. [Layout Optimizer — Space Planning AI](#9-layout-optimizer--space-planning-ai)
10. [AI Optimization Layer — Multi-Objective Optimization](#10-ai-optimization-layer--multi-objective-optimization)
11. [Authentication & Security System](#11-authentication--security-system)
12. [Database Design & Models](#12-database-design--models)
13. [API Endpoints & Request/Response Flow](#13-api-endpoints--requestresponse-flow)
14. [Frontend Components & User Interface](#14-frontend-components--user-interface)
15. [State Management Architecture](#15-state-management-architecture)
16. [Docker & Deployment Configuration](#16-docker--deployment-configuration)
17. [System Flowcharts & Diagrams](#17-system-flowcharts--diagrams)
18. [Algorithm Complexity Analysis](#18-algorithm-complexity-analysis)
19. [Testing Strategy](#19-testing-strategy)
20. [Conclusion & Future Scope](#20-conclusion--future-scope)

---

## 1. Executive Summary

### 1.1 What is ArchAI?

ArchAI is a **production-grade, web-based AI architectural planning platform** that automatically generates highly precise building designs. The system takes three primary inputs from the user:

1. **Land Numerical Dimensions** — Length, width, and area of the plot
2. **Soil/Ground Type** — The type of soil on which the building will be constructed
3. **User-Drawn Plot Shape** — A custom polygon drawn interactively on a canvas

The system then processes these inputs through multiple computational engines — **Geometry**, **Soil Analysis**, **Structural**, **Layout**, and **AI Optimization** — to produce a complete architectural design with:

- 2D Blueprint (SVG format)
- 3D Model (GLTF format)
- Structural Report (PDF)
- Load Distribution Report
- Material Estimation Report

### 1.2 Why is ArchAI Important?

| Traditional Design Problem | ArchAI Solution |
|---------------------------|-----------------|
| **Time-consuming** — Takes weeks to months | Generates designs in **seconds** |
| **Expensive** — Requires multiple professionals | Uses **deterministic algorithms** |
| **Error-prone** — Human calculations can have mistakes | Applies **engineering standards** consistently |
| **Inconsistent** — Quality varies based on designer experience | Provides **explainable outputs** with detailed calculations |

### 1.3 Key Innovation

Unlike other AI systems that use "black box" neural networks, ArchAI uses **explainable, deterministic algorithms** for all engineering calculations. Every output can be traced back to specific mathematical formulas and engineering standards.

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  React 18   │  │  TypeScript  │  │  TailwindCSS + Konva   │  │
│  │  Frontend   │  │  + Zustand   │  │  + Three.js (3D)       │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────┬────────────┘  │
│         │                │                       │               │
│         └────────────────┼───────────────────────┘               │
│                          │                                       │
│                    HTTP/REST API                                  │
│                          │                                       │
├──────────────────────────┼───────────────────────────────────────┤
│                          │            SERVER LAYER                │
│                    ┌─────┴─────┐                                  │
│                    │  FastAPI  │                                  │
│                    │  Gateway  │                                  │
│                    └─────┬─────┘                                  │
│                          │                                       │
│         ┌────────────────┼────────────────────┐                  │
│         │                │                    │                  │
│    ┌────┴────┐    ┌──────┴──────┐    ┌───────┴───────┐         │
│    │  Auth   │    │   Design    │    │   Project     │         │
│    │  API    │    │   API       │    │   API         │         │
│    └────┬────┘    └──────┬──────┘    └───────┬───────┘         │
│         │                │                    │                  │
│         │         ┌──────┴──────┐             │                  │
│         │         │  DOMAIN     │             │                  │
│         │         │  ENGINES    │             │                  │
│         │         │             │             │                  │
│         │         │ ┌─────────┐ │             │                  │
│         │         │ │Geometry │ │             │                  │
│         │         │ │ Engine  │ │             │                  │
│         │         │ └─────────┘ │             │                  │
│         │         │ ┌─────────┐ │             │                  │
│         │         │ │  Soil   │ │             │                  │
│         │         │ │ Engine  │ │             │                  │
│         │         │ └─────────┘ │             │                  │
│         │         │ ┌─────────┐ │             │                  │
│         │         │ │Structur.│ │             │                  │
│         │         │ │ Engine  │ │             │                  │
│         │         │ └─────────┘ │             │                  │
│         │         │ ┌─────────┐ │             │                  │
│         │         │ │ Layout  │ │             │                  │
│         │         │ │Optimizer│ │             │                  │
│         │         │ └─────────┘ │             │                  │
│         │         │ ┌─────────┐ │             │                  │
│         │         │ │  AI     │ │             │                  │
│         │         │ │Optimizer│ │             │                  │
│         │         │ └─────────┘ │             │                  │
│         │         └─────────────┘             │                  │
│         │                │                    │                  │
├─────────┼────────────────┼────────────────────┼──────────────────┤
│         │                │            DATA LAYER                  │
│    ┌────┴────┐    ┌──────┴──────┐    ┌───────┴───────┐         │
│    │PostgreSQL│    │   Redis     │    │   File        │         │
│    │Database │    │   Cache     │    │   Storage     │         │
│    └─────────┘    └─────────────┘    └───────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend Framework** | React 18 + TypeScript | User interface with type safety |
| **Frontend State** | Zustand | Lightweight state management |
| **Frontend Styling** | TailwindCSS | Utility-first CSS framework |
| **2D Canvas** | Konva.js (react-konva) | Interactive plot drawing |
| **3D Visualization** | Three.js + @react-three/fiber | 3D building model rendering |
| **Backend Framework** | FastAPI | High-performance async API |
| **Backend Language** | Python 3.12 | Core computation language |
| **Database** | PostgreSQL 15 | Persistent data storage |
| **Cache** | Redis 7 | Session & computation cache |
| **ORM** | SQLAlchemy 2.0 (Async) | Database abstraction |
| **Task Queue** | Celery + Redis | Background job processing |
| **Containerization** | Docker + Docker Compose | Environment consistency |
| **Scientific Computing** | NumPy, SciPy, Shapely | Mathematical computations |

---

## 3. Project Structure & Directory Layout

### 3.1 Complete Directory Tree

```
Architechure/
├── backend/                          # Python Backend Application
│   ├── app/                          # Main Application Package
│   │   ├── __init__.py              # Package initializer
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── api/                     # API Route Handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   └── design.py           # Design generation endpoints
│   │   ├── core/                    # Core Configuration & Utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Application settings (Pydantic)
│   │   │   ├── database.py         # SQLAlchemy async DB setup
│   │   │   ├── deps.py             # FastAPI dependency injection
│   │   │   └── security.py         # JWT & password hashing
│   │   ├── domains/                 # Domain-Specific Engines
│   │   │   ├── __init__.py
│   │   │   ├── geometry/           # Geometric calculations
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py       # Shoelace theorem, centroids, etc.
│   │   │   ├── soil/               # Soil analysis engine
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py       # Bearing capacity, settlement
│   │   │   ├── structural/         # Structural engineering
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py       # Beam, column, load analysis
│   │   │   ├── layout/             # Layout optimization
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py       # Room placement, adjacency
│   │   │   ├── optimization/       # AI optimization layer
│   │   │   │   ├── __init__.py
│   │   │   │   └── engine.py       # Genetic algorithm, scoring
│   │   │   └── rendering/          # 2D/3D rendering engine
│   │   │       └── __init__.py
│   │   ├── models/                  # SQLAlchemy Database Models
│   │   │   ├── __init__.py
│   │   │   └── user.py             # User, Project, Design models
│   │   ├── schemas/                 # Pydantic Request/Response Schemas
│   │   │   ├── __init__.py
│   │   │   └── design.py           # Design API schemas
│   │   ├── services/                # Business Logic Services
│   │   │   └── __init__.py
│   │   └── utils/                   # Utility Functions
│   │       └── __init__.py
│   ├── tests/                       # Test Suite
│   │   ├── integration/            # Integration tests
│   │   └── unit/                   # Unit tests
│   │       └── test_geometry.py
│   ├── requirements.txt             # Python dependencies
│   └── archai.db                    # SQLite development database
│
├── frontend/                         # React Frontend Application
│   ├── src/
│   │   ├── App.tsx                  # Root component with routing
│   │   ├── main.tsx                 # Application entry point
│   │   ├── index.css               # Global styles
│   │   ├── components/
│   │   │   ├── drawing/
│   │   │   │   └── PlotDrawing.tsx  # Interactive polygon drawer
│   │   │   ├── viewer/
│   │   │   │   └── BuildingViewer.tsx # 3D building viewer
│   │   │   ├── layout/
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx        # Authentication page
│   │   │   ├── DashboardPage.tsx    # Project dashboard
│   │   │   └── DesignPage.tsx       # Main design interface
│   │   ├── services/
│   │   │   └── api.ts              # API client with interceptors
│   │   ├── store/
│   │   │   └── index.ts            # Zustand state stores
│   │   └── types/
│   │       └── index.ts            # TypeScript type definitions
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docker/                           # Docker Configuration
│   ├── docker-compose.yml          # Multi-container orchestration
│   ├── Dockerfile.backend           # Backend container definition
│   └── Dockerfile.frontend          # Frontend container definition
│
├── docs/                            # Documentation
├── scripts/                         # Build & utility scripts
└── pyproject.toml                   # Python project configuration
```

### 3.2 Module Dependency Graph

```
┌─────────────┐
│  main.py    │ ◄─── FastAPI Application Entry Point
└──────┬──────┘
       │
       ├──► api/auth.py        (Authentication Routes)
       ├──► api/design.py      (Design Routes)
       │
       ├──► core/config.py     (Settings Management)
       ├──► core/database.py   (Database Connection)
       ├──► core/deps.py       (Dependency Injection)
       ├──► core/security.py   (JWT & Password Hashing)
       │
       ├──► domains/geometry/engine.py    (Geometric Calculations)
       ├──► domains/soil/engine.py        (Soil Analysis)
       ├──► domains/structural/engine.py  (Structural Analysis)
       ├──► domains/layout/engine.py      (Layout Optimization)
       └──► domains/optimization/engine.py (AI Optimization)
                │
                ├──► (imports) geometry/engine.py
                ├──► (imports) soil/engine.py
                ├──► (imports) structural/engine.py
                └──► (imports) layout/engine.py
```

---

## 4. Backend Architecture Deep Dive

### 4.1 FastAPI Application Entry Point (`main.py`)

The `main.py` file is the heart of the backend application. It creates the FastAPI instance, configures middleware, handles errors, and registers all API routes.

```python
# ═══════════════════════════════════════════════════════════════
# ArchAI Platform - Main Application
# Developer: Satya Narayan Sahu
# ═══════════════════════════════════════════════════════════════

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import auth, design

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup (database init) and shutdown (cleanup) events.
    """
    await init_db()  # Create database tables on startup
    yield
    await close_db()  # Close connections on shutdown

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Architectural Planning Platform",
    lifespan=lifespan,
)

# CORS Middleware - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(design.router, prefix=settings.API_V1_PREFIX)
```

**Key Concepts Explained:**

1. **`asynccontextmanager`**: This is Python's way of managing resources that need setup and cleanup. When the server starts, it connects to the database. When it shuts down, it closes the connection.

2. **CORS (Cross-Origin Resource Sharing)**: Since our frontend runs on port 5173 and backend on port 8000, they are on different "origins." CORS middleware allows the browser to make requests from the frontend to the backend.

3. **Router**: FastAPI routers group related endpoints together. We have `auth.router` for login/register and `design.router` for design generation.

### 4.2 Application Configuration (`core/config.py`)

The configuration module uses **Pydantic Settings** to manage all environment variables and application settings in a type-safe manner.

| Setting Category | Setting Name | Default Value | Description |
|-----------------|-------------|---------------|-------------|
| **Application** | `APP_NAME` | "ArchAI Platform" | Application display name |
| | `APP_VERSION` | "1.0.0" | Current version number |
| | `DEBUG` | False | Enable debug mode |
| | `API_V1_PREFIX` | "/api/v1" | API version prefix |
| **Security** | `SECRET_KEY` | "your-super-secret-key" | JWT signing secret |
| | `ALGORITHM` | "HS256" | JWT signing algorithm |
| | `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token lifetime |
| | `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token lifetime |
| **Database** | `DATABASE_URL` | "sqlite+aiosqlite:///./archai.db" | Database connection string |
| | `DATABASE_POOL_SIZE` | 20 | Connection pool size |
| **Redis** | `REDIS_URL` | "redis://localhost:6379/0" | Redis connection URL |
| | `CACHE_EXPIRE_SECONDS` | 3600 | Cache TTL in seconds |
| **Engineering** | `DEFAULT_SAFETY_FACTOR` | 1.5 | Structural safety factor |
| | `CONCRETE_UNIT_WEIGHT` | 24.0 kN/m³ | Concrete density |
| | `STEEL_UNIT_WEIGHT` | 78.5 kN/m³ | Steel density |

### 4.3 Database Configuration (`core/database.py`)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `echo` | `settings.DEBUG` | Log SQL queries in debug mode |
| `pool_size` | 20 | Number of connections to keep open |
| `max_overflow` | 10 | Extra connections when pool is full |

**Connection Pooling Explained:**
- Instead of opening a new database connection for every request (slow), we keep 20 connections open
- If 25 requests come simultaneously, 5 extra "overflow" connections are created
- This dramatically improves performance under load

---

## 5. Frontend Architecture Deep Dive

### 5.1 React Application Structure

The frontend is built with **React 18**, **TypeScript**, and **Vite** for blazing-fast development.

| Directory | File | Purpose |
|-----------|------|---------|
| `src/` | `App.tsx` | Root component with routing |
| | `main.tsx` | Entry point (renders App) |
| | `index.css` | TailwindCSS imports |
| `src/components/drawing/` | `PlotDrawing.tsx` | Interactive canvas for plot drawing |
| `src/components/viewer/` | `BuildingViewer.tsx` | 3D Three.js viewer |
| `src/pages/` | `LoginPage.tsx` | Login/Register forms |
| | `DashboardPage.tsx` | Project list |
| | `DesignPage.tsx` | Main design interface |
| `src/services/` | `api.ts` | Axios API client |
| `src/store/` | `index.ts` | Zustand state stores |
| `src/types/` | `index.ts` | TypeScript interfaces |

### 5.2 Routing Configuration

| Route | Component | Description |
|-------|-----------|-------------|
| `/login` | `LoginPage` | Shows login/register page |
| `/` | `DashboardPage` | Shows dashboard with project list |
| `/design` | `DesignPage` | Shows empty design interface (new project) |
| `/design/:projectId` | `DesignPage` | Loads existing project |
| `*` | Redirect to `/` | Redirects to dashboard for unknown routes |

### 5.3 API Service Layer (`services/api.ts`)

The API client uses **Axios** with automatic token management and refresh logic.

**Token Refresh Flow:**

| Step | Action | Result |
|------|--------|--------|
| 1 | User makes a request with an expired token | Request sent |
| 2 | Server returns 401 Unauthorized | Error caught |
| 3 | Interceptor catches the error | Auto-retry triggered |
| 4 | Calls `/auth/refresh` with the refresh token | New token requested |
| 5 | Gets new access token | Token refreshed |
| 6 | Retries the original request with new token | Request succeeds |
| 7 | User never notices the token expired | Seamless experience |

---

## 6. Geometry Engine — Algorithms & Mathematics

### 6.1 Overview

The Geometry Engine is the foundational module that handles all geometric calculations for architectural planning. It implements precise mathematical algorithms for polygon operations.

### 6.2 Core Data Structures

| Structure | Attributes | Methods |
|-----------|-----------|---------|
| `Point2D` | `x: float`, `y: float` | `distance_to()`, `to_tuple()`, `to_array()` |
| `Polygon` | `vertices: List[Point2D]` | `calculate_area()`, `calculate_centroid()`, `is_valid()`, `calculate_perimeter()` |

### 6.3 Polygon Area Calculation — Shoelace Theorem

The **Shoelace Theorem** (also called Gauss's Area Formula) is one of the most elegant algorithms for calculating the area of a simple polygon.

#### Mathematical Formula:

```
Given a polygon with vertices (x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ):

A = ½|Σᵢ₌₁ⁿ (xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)|

where (xₙ₊₁,yₙ₊₁) = (x₁,y₁) to close the polygon
```

#### Why is it called "Shoelace"?

If you write the coordinates in two columns and draw diagonal lines connecting them, it looks like the criss-cross pattern of lacing a shoe:

```
x₁  y₁
 \ /
  X
 / \
x₂  y₂
 \ /
  X
 / \
x₃  y₃
```

#### Step-by-Step Example:

| Step | Calculation | Result |
|------|-------------|--------|
| 1 | x₁y₂ - x₂y₁ = 0×0 - 20×0 | 0 |
| 2 | x₂y₃ - x₃y₂ = 20×15 - 20×0 | 300 |
| 3 | x₃y₄ - x₄y₃ = 20×15 - 0×15 | 300 |
| 4 | x₄y₁ - x₁y₄ = 0×0 - 0×15 | 0 |
| **Sum** | 0 + 300 + 300 + 0 | **600** |
| **Area** | \|600\| / 2 | **300 m²** ✓ |

### 6.4 Compactness Ratio

| Value | Shape Type | Description |
|-------|-----------|-------------|
| Q = 1.0 | Circle | Perfectly compact |
| Q < 1.0 | All other shapes | Less compact |
| Q → 0 | Very elongated shapes | Least compact |

---

## 7. Soil Analysis Engine — Geotechnical Engineering

### 7.1 Overview

The Soil Analysis Engine applies **geotechnical engineering principles** to determine foundation requirements based on soil properties.

### 7.2 Soil Classification

| Soil Type | Grain Size | Characteristics | Foundation Suitability |
|-----------|-----------|-----------------|----------------------|
| **Rocky** | >300mm | Bedrock, highest bearing | Excellent |
| **Gravel** | 4.75-75mm | Very coarse, excellent bearing | Very Good |
| **Sand** | 0.075-4.75mm | Coarse-grained, non-cohesive | Good |
| **Loam** | Mixed | Moderate properties | Good |
| **Mixed** | Combination | Variable properties | Moderate |
| **Clay** | <0.002mm | Fine-grained, cohesive | Moderate (settlement concerns) |
| **Silt** | <0.075mm | Fine-grained, low plasticity | Poor (liquefaction risk) |
| **Peat** | Organic | Very poor for foundations | Very Poor |

### 7.3 Default Soil Properties

| Soil Type | Bearing Capacity (kN/m²) | Cohesion (kN/m²) | Friction Angle (°) | Unit Weight (kN/m³) | Permeability (m/s) |
|-----------|--------------------------|-------------------|-------------------|---------------------|-------------------|
| **Rocky** | 1000 | 100 | 45 | 25.0 | 1e-5 |
| **Gravel** | 450 | 0 | 38 | 20.0 | 1e-2 |
| **Sand** | 250 | 0 | 32 | 19.0 | 1e-4 |
| **Loam** | 180 | 15 | 25 | 18.5 | 1e-6 |
| **Mixed** | 200 | 12 | 28 | 18.5 | 1e-5 |
| **Clay** | 150 | 25 | 5 | 18.0 | 1e-9 |
| **Silt** | 100 | 10 | 28 | 17.5 | 1e-7 |
| **Peat** | 30 | 5 | 10 | 12.0 | 1e-6 |

### 7.4 Bearing Capacity Calculation — Terzaghi's Method

**Karl von Terzaghi** (1883-1963) is known as the "Father of Soil Mechanics." His bearing capacity equation is the foundation of all foundation design.

#### General Bearing Capacity Equation:

| Symbol | Description | Units |
|--------|-------------|-------|
| `qu` | Ultimate bearing capacity | kN/m² |
| `c` | Soil cohesion | kN/m² |
| `Nc, Nq, Nγ` | Bearing capacity factors | Dimensionless |
| `q` | Surcharge pressure (γ × Df) | kN/m² |
| `γ` | Unit weight of soil | kN/m³ |
| `B` | Foundation width | m |
| `Sc, Sq, Sγ` | Shape factors | Dimensionless |

#### Bearing Capacity Factors Formula:

| Factor | Formula | Description |
|--------|---------|-------------|
| `Nq` | `e^(π×tanφ) × tan²(45° + φ/2)` | Surcharge factor |
| `Nc` | `(Nq - 1) × cot(φ)` [for φ > 0] | Cohesion factor |
| `Nγ` | `2 × (Nq + 1) × tan(φ)` | Unit weight factor |

#### Example Calculation for Sand (φ = 32°):

| Step | Calculation | Result |
|------|-------------|--------|
| 1 | Convert φ to radians: 32° × π/180 | 0.5585 rad |
| 2 | Calculate Nq: e^(π×tan(32°)) × tan²(61°) | 22.61 |
| 3 | Calculate Nc: (22.61 - 1) / tan(32°) | 34.58 |
| 4 | Calculate Nγ: 2 × 23.61 × tan(32°) | 29.51 |
| 5 | Calculate qu (B=2m, Df=1m) | 990.3 kN/m² |

### 7.5 Foundation Selection Criteria

| Condition | Foundation Type | Typical Depth |
|-----------|----------------|---------------|
| q_req < 50% BC AND BC > 300 | Shallow Isolated | 0.6-1.0m |
| q_req < 50% BC AND BC ≤ 300 | Shallow Strip | 0.6-1.2m |
| q_req < 80% BC AND stories > 3 | Shallow Raft | 1.0-1.5m |
| q_req < 80% BC AND stories ≤ 3 | Shallow Strip | 0.9-1.2m |
| BC < 100 kN/m² | Deep Pile | 8-15m |
| Otherwise | Mat Foundation | 1.0-2.0m |

---

## 8. Structural Solver — Engineering Calculations

### 8.1 Overview

The Structural Solver performs **load analysis, beam design, column design, and safety verification** following structural engineering principles.

### 8.2 Load Types

| Load Category | Load Type | Description | Load Factor |
|--------------|-----------|-------------|-------------|
| **Permanent** | Dead (DL) | Structure self-weight, finishes, fixed equipment | 1.4 |
| **Variable** | Live (LL) | Occupants, furniture, vehicles | 1.6 |
| **Environmental** | Wind (WL) | Lateral wind pressure | 1.4 |
| | Seismic (EL) | Earthquake forces | 1.0 |
| | Snow (SL) | Roof snow load | 1.5 |

### 8.3 Material Properties Comparison

| Property | Concrete (C25) | Steel (Fe250) | Timber | Reinforced Concrete |
|----------|---------------|---------------|--------|-------------------|
| **Compressive Strength** | 25 MPa | 250 MPa | 12 MPa | 30 MPa |
| **Tensile Strength** | 2.5 MPa | 400 MPa | 8 MPa | 3.0 MPa |
| **Yield Strength** | — | 250 MPa | — | 415 MPa (steel) |
| **Elastic Modulus** | 25 GPa | 200 GPa | 12 GPa | 29 GPa |
| **Unit Weight** | 24 kN/m³ | 78.5 kN/m³ | 6 kN/m³ | 25 kN/m³ |
| **Poisson's Ratio** | 0.2 | 0.3 | 0.35 | 0.2 |

### 8.4 Beam Bending Analysis

| Support Type | Load Type | Max Moment | Max Shear | Max Deflection |
|-------------|-----------|------------|-----------|----------------|
| Simply Supported | UDL | wL²/8 | wL/2 | 5wL⁴/(384EI) |
| Simply Supported | Point Load (center) | PL/4 | P/2 | PL³/(48EI) |
| Cantilever | UDL | wL²/2 | wL | wL⁴/(8EI) |
| Cantilever | Point Load (end) | PL | P | PL³/(3EI) |
| Fixed Beam | UDL | wL²/12 | wL/2 | wL⁴/(384EI) |

### 8.5 Deflection Limits

| Application | Limit | Description |
|-------------|-------|-------------|
| Floors | L/360 | Span divided by 360 |
| Roofs | L/240 | Span divided by 240 |
| Cantilevers | L/180 | Span divided by 180 |

---

## 9. Layout Optimizer — Space Planning AI

### 9.1 Overview

The Layout Optimizer uses **constraint-based algorithms** to arrange rooms within the buildable area, considering adjacency, ventilation, daylight, and circulation.

### 9.2 Room Type Requirements

| Room Type | Min Area (m²) | Max Area (m²) | Min Width (m) | Min Light (%) | Ventilation | Preferred Orientation |
|-----------|--------------|---------------|---------------|---------------|-------------|---------------------|
| Living Room | 12.0 | 40.0 | 3.0 | 12% | Required | South |
| Bedroom | 9.0 | 25.0 | 2.7 | 10% | Required | South |
| Kitchen | 6.0 | 20.0 | 2.0 | 8% | Required | East |
| Bathroom | 3.5 | 10.0 | 1.5 | 5% | Required | North |
| Dining | 8.0 | 20.0 | 2.5 | 10% | Required | Southeast |
| Study | 6.0 | 15.0 | 2.0 | 10% | Required | North |
| Entrance | 3.0 | 10.0 | 1.2 | 5% | Required | — |
| Corridor | 2.0 | 15.0 | 0.9 | 0% | Not Required | — |
| Utility | 2.0 | 8.0 | 1.5 | 5% | Required | — |
| Storage | 1.5 | 10.0 | 0.8 | 0% | Not Required | — |
| Garage | 15.0 | 40.0 | 3.0 | 0% | Required | — |
| Balcony | 3.0 | 15.0 | 1.0 | 100% | Required | South |

### 9.3 Daylight Factor Calculation

| Symbol | Description | Default Value |
|--------|-------------|---------------|
| `A_g` | Glazing (window) area | m² |
| `θ` | Angle of visible sky | 60° |
| `τ` | Light transmittance | 0.7 (double glazing) |
| `f_o` | Orientation factor | Varies by direction |
| `A` | Room floor area | m² |
| `R` | Average surface reflectance | 0.5 |

#### Orientation Factors (Northern Hemisphere):

| Orientation | Factor | Sunlight Level |
|-------------|--------|---------------|
| South | 1.2 | Maximum |
| Southeast | 1.1 | High |
| Southwest | 1.1 | High |
| East | 0.9 | Moderate |
| West | 0.9 | Moderate |
| Northeast | 0.7 | Low |
| Northwest | 0.7 | Low |
| North | 0.6 | Minimum |

#### Daylight Factor Ranges:

| DF Range | Quality | Lighting Need |
|----------|---------|---------------|
| > 5% | Excellent | Could be too bright |
| 2-5% | Good | Ideal range |
| 1-2% | Adequate | Supplementary lighting helpful |
| < 1% | Poor | Artificial lighting required |

### 9.4 Ventilation Scoring Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Cross Ventilation | 40 | Windows on opposite walls |
| Window-to-Floor Ratio (10-20%) | 30 | Optimal glazing ratio |
| Room Depth ≤ 6m | 30 | Shallower rooms ventilate better |
| **Maximum Score** | **100** | |

---

## 10. AI Optimization Layer — Multi-Objective Optimization

### 10.1 Overview

The AI Optimization Layer combines all domain engines and uses **multi-objective optimization** to find the best design that balances competing objectives.

### 10.2 Optimization Objectives

| Objective | Description | Trade-off |
|-----------|-------------|-----------|
| **Cost** | Minimize construction cost | Stronger structures cost more |
| **Stability** | Maximize structural safety | Higher safety = more material |
| **Ventilation** | Maximize air flow | More windows = less wall space |
| **Daylight** | Maximize natural light | Larger windows = heat gain |
| **Space Utilization** | Maximize usable area | More rooms = less circulation |
| **Aesthetics** | Visual appeal | Subjective measure |
| **Energy Efficiency** | Minimize energy use | Compact shapes limit design |

### 10.3 Optimization Weights

| Objective | Default Weight | Priority Level |
|-----------|---------------|---------------|
| **Stability** | 0.25 | Highest — Safety first! |
| **Cost** | 0.15 | Medium |
| **Ventilation** | 0.15 | Medium |
| **Daylight** | 0.15 | Medium |
| **Space Utilization** | 0.15 | Medium |
| **Aesthetics** | 0.15 | Medium |
| **Total** | **1.00** | Normalized |

### 10.4 Genetic Algorithm Parameters

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `population_size` | 50 | Number of solutions per generation |
| `generations` | 100 | Number of evolution iterations |
| `mutation_rate` | 0.1 (10%) | Probability of random change |
| `crossover_rate` | 0.8 (80%) | Probability of combining parents |
| `elitism` | 2 | Number of best solutions to preserve |

### 10.5 Design Scoring Components

| Score | Range | Calculation Basis | Optimal Range |
|-------|-------|-------------------|---------------|
| **Safety Score** | 0-100 | Structural utilization ratio | > 80 |
| **Stability Score** | 0-100 | Foundation settlement | > 85 |
| **Material Efficiency** | 0-100 | Utilization in 0.7-0.85 range | 70-85 |
| **Space Utilization** | 0-100 | Built area / plot area | 60-80% |
| **Ventilation Score** | 0-100 | Cross-ventilation & window ratios | > 70 |
| **Daylight Score** | 0-100 | Daylight factor calculations | 2-5% DF |
| **Cost Efficiency** | 0-100 | Settlement & design efficiency | > 75 |
| **Overall Score** | 0-100 | Weighted average | > 80 |

---

## 11. Authentication & Security System

### 11.1 Overview

The authentication system uses **JWT (JSON Web Tokens)** with **bcrypt** password hashing for secure user management.

### 11.2 Password Hashing Process

| Step | Action | Description |
|------|--------|-------------|
| 1 | Generate salt | Random 22-character string |
| 2 | Combine | Password + salt |
| 3 | Hash | Blowfish cipher × 4096 rounds |
| 4 | Store | Algorithm + cost + salt + hash |

**Security Features:**

| Feature | Protection |
|---------|------------|
| Unique salt per password | Prevents rainbow table attacks |
| Cost factor (12) | Makes brute force impractical |
| Adaptive hashing | Can increase rounds as hardware improves |

### 11.3 JWT Token Structure

| Component | Content | Encoding |
|-----------|---------|----------|
| **Header** | `{"alg": "HS256", "typ": "JWT"}` | Base64 |
| **Payload** | `{"sub": "user-id", "exp": timestamp, "type": "access"}` | Base64 |
| **Signature** | `HMAC-SHA256(HEADER + PAYLOAD, SECRET_KEY)` | Binary |

### 11.4 Token Types

| Token Type | Lifetime | Purpose | Storage |
|------------|----------|---------|---------|
| **Access Token** | 30 minutes | Authenticate API requests | Memory/State |
| **Refresh Token** | 7 days | Get new access tokens | localStorage |

---

## 12. Database Design & Models

### 12.1 Entity Relationship

| Entity | Primary Key | Foreign Keys | Relationships |
|--------|-------------|--------------|---------------|
| **Users** | `id (UUID)` | — | Has many Projects |
| **Projects** | `id (UUID)` | `owner_id → Users.id` | Belongs to User, Has many Designs |
| **Designs** | `id (UUID)` | `project_id → Projects.id` | Belongs to Project |

### 12.2 User Model Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PK, UUID | Unique identifier |
| `email` | String(255) | UNIQUE, INDEX | Login email |
| `hashed_password` | String(255) | NOT NULL | bcrypt hash |
| `full_name` | String(255) | NULLABLE | Display name |
| `role` | String(50) | DEFAULT "viewer" | Permission level |
| `is_active` | Boolean | DEFAULT TRUE | Account status |
| `is_superuser` | Boolean | DEFAULT FALSE | Admin privileges |
| `created_at` | DateTime | AUTO | Creation timestamp |
| `updated_at` | DateTime | AUTO | Last update timestamp |

### 12.3 Project Model Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PK, UUID | Unique identifier |
| `name` | String(255) | NOT NULL | Project name |
| `description` | Text | NULLABLE | Project description |
| `owner_id` | String(36) | FK, NOT NULL | Owner user ID |
| `status` | String(50) | DEFAULT "draft" | Project status |
| `settings` | Text | NULLABLE | JSON settings |
| `created_at` | DateTime | AUTO | Creation timestamp |
| `updated_at` | DateTime | AUTO | Last update timestamp |

### 12.4 Design Model Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PK, UUID | Unique identifier |
| `project_id` | String(36) | FK, NOT NULL | Parent project ID |
| `name` | String(255) | NOT NULL | Design name |
| `design_data` | Text | NOT NULL | JSON design data |
| `scores` | Text | NULLABLE | JSON quality scores |
| `status` | String(50) | DEFAULT "generated" | Design status |
| `created_at` | DateTime | AUTO | Creation timestamp |

---

## 13. API Endpoints & Request/Response Flow

### 13.1 Authentication Endpoints

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/auth/register` | POST | Create new user account | No |
| `/auth/login` | POST | Get access tokens | No |
| `/auth/refresh` | POST | Refresh expired token | No |
| `/auth/me` | GET | Get current user info | Yes |
| `/auth/logout` | POST | Logout user | Yes |

### 13.2 Design Endpoints

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/design/validate-plot` | POST | Validate plot polygon | Yes |
| `/design/analyze-soil` | POST | Analyze soil & foundation | Yes |
| `/design/generate` | POST | Generate architectural design | Yes |
| `/design/projects` | GET | List user projects | Yes |
| `/design/projects` | POST | Create new project | Yes |
| `/design/projects/{id}` | GET | Get specific project | Yes |
| `/design/export` | POST | Export design (SVG/GLTF/PDF) | Yes |

### 13.3 Design Generation Pipeline

| Step | Engine | Input | Output |
|------|--------|-------|--------|
| 1 | Geometry Engine | Plot coordinates | Validated polygon + properties |
| 2 | Soil Engine | Soil type | Foundation recommendation |
| 3 | Layout Engine | Room requirements | Room placements |
| 4 | Structural Engine | Load data | Beam/column specifications |
| 5 | Optimization Engine | All above | Quality scores |

---

## 14. Frontend Components & User Interface

### 14.1 Plot Drawing Features

| Feature | Description | User Action |
|---------|-------------|-------------|
| Click to Add Vertices | Each click adds a polygon point | Click on canvas |
| Drag to Move Vertices | Reposition points by dragging | Drag vertex |
| Grid Snapping | Points snap to 10m grid | Automatic |
| Real-time Area | Shoelace theorem calculated live | Automatic |
| Zoom & Pan | Navigate the canvas | Mouse wheel / Drag |
| Auto-close | Click first point to close polygon | Click first vertex |

### 14.2 Room Color Coding

| Room Type | Color | Hex Code |
|-----------|-------|----------|
| Living Room | Blue | `#3b82f6` |
| Bedroom | Purple | `#8b5cf6` |
| Kitchen | Amber | `#f59e0b` |
| Bathroom | Cyan | `#06b6d4` |
| Dining | Green | `#10b981` |
| Study | Indigo | `#6366f1` |
| Garage | Gray | `#6b7280` |
| Storage | Light Gray | `#9ca3af` |
| Utility | Orange | `#f97316` |
| Entrance | Lime | `#84cc16` |
| Corridor | Light Gray | `#d1d5db` |
| Balcony | Light Green | `#a3e635` |

---

## 15. State Management Architecture

### 15.1 Zustand Stores Overview

| Store | State Properties | Key Actions |
|-------|-----------------|-------------|
| **AuthStore** | `user`, `isAuthenticated`, `isLoading` | `setUser()`, `logout()` |
| **DesignStore** | `currentDesign`, `currentProject`, `isGenerating`, `error` | `setCurrentDesign()`, `setGenerating()`, `setError()` |
| **DrawingStore** | `points`, `isDrawing`, `isClosed`, `selectedPointIndex` | `addPoint()`, `updatePoint()`, `removePoint()`, `closePolygon()`, `clearDrawing()` |
| **ViewStore** | `zoom`, `pan`, `showGrid`, `showMeasurements` | `setZoom()`, `zoomIn()`, `zoomOut()`, `toggleGrid()`, `resetView()` |
| **UIStore** | `sidebarOpen`, `activePanel`, `modalOpen` | `toggleSidebar()`, `setActivePanel()`, `openModal()`, `closeModal()` |

### 15.2 Zustand vs Redux Comparison

| Aspect | Zustand | Redux |
|--------|---------|-------|
| **Boilerplate** | Minimal | Extensive |
| **TypeScript** | First-class support | Requires extra setup |
| **Bundle Size** | ~1KB | ~16KB |
| **Learning Curve** | Low | Medium-High |
| **API Complexity** | Simple (`useStore()`) | Complex (actions, reducers, dispatch) |
| **Middleware** | Built-in persist | Requires redux-thunk/saga |

---

## 16. Docker & Deployment Configuration

### 16.1 Docker Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **db** | postgres:15-alpine | 5432 | PostgreSQL database |
| **redis** | redis:7-alpine | 6379 | Cache & session store |
| **backend** | Custom (Python 3.12) | 8000 | FastAPI application |
| **frontend** | Custom (Node 20) | 5173 | Vite dev server |

### 16.2 Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | backend | PostgreSQL connection string |
| `REDIS_URL` | backend | Redis connection URL |
| `SECRET_KEY` | backend | JWT signing secret |
| `DEBUG` | backend | Enable debug mode |
| `VITE_API_URL` | frontend | Backend API URL |

---

## 17. System Flowcharts & Diagrams

### 17.1 Authentication Flow

| Step | Actor | Action | Result |
|------|-------|--------|--------|
| 1 | User | Submit login form | Credentials sent |
| 2 | FastAPI | Query database | User record found |
| 3 | FastAPI | bcrypt.verify() | Password match confirmed |
| 4 | JWT Service | create_access_token() | Token generated |
| 5 | FastAPI | Return response | Tokens sent to client |
| 6 | Client | Store in localStorage | Ready for API calls |

### 17.2 Design Generation Flow

| Step | Engine | Processing | Output |
|------|--------|------------|--------|
| 1 | Geometry | Validate polygon, calculate area | Valid plot + properties |
| 2 | Soil | Get bearing capacity, recommend foundation | Foundation design |
| 3 | Layout | Place rooms, check adjacencies | Room placements |
| 4 | Structural | Calculate loads, design beams/columns | Structural specs |
| 5 | Optimization | Score design, calculate quality metrics | Quality scores |
| 6 | Export | Generate SVG/GLTF/PDF | Downloadable files |

---

## 18. Algorithm Complexity Analysis

### 18.1 Time & Space Complexity

| Algorithm | Operation | Time Complexity | Space Complexity |
|-----------|-----------|----------------|------------------|
| **Shoelace Area** | Polygon area | O(n) | O(1) |
| **Centroid** | Center of mass | O(n) | O(1) |
| **Perimeter** | Edge lengths | O(n) | O(1) |
| **Convexity Check** | Cross product test | O(n) | O(1) |
| **Point-in-Polygon** | Ray casting | O(n) | O(1) |
| **Setback** | Buffer operation | O(n log n) | O(n) |
| **Bearing Capacity** | Terzaghi factors | O(1) | O(1) |
| **Settlement** | Elastic + consolidation | O(1) | O(1) |
| **Beam Analysis** | Load distribution | O(m) | O(1) |
| **Room Placement** | Grid-based | O(r) | O(r) |
| **Adjacency Detection** | Pairwise comparison | O(r²) | O(r²) |
| **Daylight Calc** | Per room | O(r) | O(1) |
| **Genetic Algorithm** | Full optimization | O(g × p × n) | O(p × n) |

**Legend:** n = vertices, r = rooms, m = loads, g = generations, p = population

### 18.2 Performance Rating

| Algorithm | Rating | Speed |
|-----------|--------|-------|
| Bearing Capacity | ████████░░ | Very Fast (O(1)) |
| Shoelace Area | ██████░░░░ | Fast (O(n)) |
| Centroid | ██████░░░░ | Fast (O(n)) |
| Room Placement | █████░░░░░ | Moderate (O(r)) |
| Adjacency Check | ████░░░░░░ | Can be slow (O(r²)) |
| Genetic Algorithm | ███░░░░░░░ | Slowest but powerful |

---

## 19. Testing Strategy

### 19.1 Test Coverage Targets

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| Geometry Engine | 95% | Critical |
| Soil Engine | 90% | High |
| Structural Engine | 90% | High |
| Layout Engine | 85% | Medium |
| Optimization Engine | 80% | Medium |
| API Endpoints | 90% | High |
| Auth System | 95% | Critical |

### 19.2 Test Types

| Test Type | Scope | Tools | Frequency |
|-----------|-------|-------|-----------|
| Unit Tests | Individual functions | pytest | Every commit |
| Integration Tests | API endpoints | pytest-asyncio | Every PR |
| E2E Tests | Full user flows | Playwright | Daily |
| Performance Tests | Load testing | Locust | Weekly |

---

## 20. Conclusion & Future Scope

### 20.1 Key Achievements

| Achievement | Description |
|-------------|-------------|
| ✅ Deterministic Design | Same input always produces same output |
| ✅ Real-time Validation | Instant feedback on plot geometry |
| ✅ Comprehensive Scoring | 8 different quality metrics |
| ✅ 3D Visualization | Interactive Three.js building viewer |
| ✅ Multiple Export Formats | SVG, GLTF, PDF, JSON |
| ✅ Secure Authentication | JWT with bcrypt password hashing |
| ✅ Containerized Deployment | Docker Compose for easy setup |

### 20.2 Future Enhancements

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Machine Learning** | Train neural network on design patterns | High | Large |
| **Multi-floor Layout** | Stacked floor optimization | High | Medium |
| **Cost Estimation** | Detailed material quantity calculation | Medium | Medium |
| **Code Compliance** | Auto-check against local building codes | Medium | Large |
| **Collaborative Design** | Real-time multi-user editing | Low | Large |
| **AR Visualization** | Augmented reality building preview | Low | Large |
| **BIM Integration** | Export to Industry Foundation Classes | Low | Large |

### 20.3 Formulas Summary

| Domain | Formula | Description |
|--------|---------|-------------|
| **Geometry** | `A = ½\|Σ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)\|` | Shoelace area |
| | `Cx = (1/6A) × Σ(xᵢ+xᵢ₊₁)(cross)` | Centroid X |
| | `Q = 4πA/P²` | Compactness |
| **Soil** | `qu = cNcSc + qNqSq + 0.5γBNγSγ` | Bearing capacity |
| | `Nq = e^(πtanφ) × tan²(45+φ/2)` | Nq factor |
| **Structural** | `M = wL²/8` | Beam moment (UDL) |
| | `δ = 5wL⁴/(384EI)` | Beam deflection |
| | `σ = M/Z` | Bending stress |
| **Daylight** | `DF = (A_g × θ × τ × f_o) / (A × (1-R²))` | Daylight factor |

---

## 📚 Document Information

| Field | Details |
|-------|---------|
| **Document Prepared By** | Satya Narayan Sahu & Tathoi Mondal |
| **Date** | January 2026 |
| **Version** | 1.0.0 |
| **Platform** | ArchAI — AI-Powered Architectural Planning System |

---

*© 2026 ArchAI Platform. All Rights Reserved.*