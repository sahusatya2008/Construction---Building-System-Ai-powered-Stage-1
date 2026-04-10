# ArchAI Platform

**AI-Powered Architectural Planning System**

A production-grade, web-based AI architectural planning platform that generates highly precise building designs based on land dimensions, soil analysis, user-drawn plot shapes, and regulatory constraints.

## 🏗️ Features

### Core Engines

1. **Geometry Engine**
   - Polygon validation (non-self-intersecting, closed)
   - Area calculation using Shoelace theorem
   - Centroid calculation
   - Setback polygon generation
   - Coordinate transformations

2. **Soil Analysis Engine**
   - Bearing capacity calculation (Terzaghi's method)
   - Foundation type recommendations
   - Settlement estimation
   - Soil compatibility analysis

3. **Structural Solver**
   - Load calculations (dead, live, wind, seismic)
   - Beam bending analysis
   - Column design
   - Structural safety checks

4. **Layout Optimizer**
   - Room adjacency graph modeling
   - Space allocation optimization
   - Ventilation flow analysis
   - Daylight simulation

5. **AI Optimization Layer**
   - Multi-objective optimization
   - Genetic Algorithm for layout optimization
   - Explainable AI outputs
   - Design scoring and evaluation

### Output Formats

- 2D Blueprint (SVG)
- 3D Model (GLTF)
- Structural Report (PDF)
- Load Distribution Report
- Material Estimation Report

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/archai.git
cd archai

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/v1/docs
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/archai_db"
export SECRET_KEY="your-super-secret-key"

# Run the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📐 API Documentation

### Authentication

```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Design Generation

```bash
# Validate plot
POST /api/v1/design/validate-plot
{
  "coordinates": [
    {"x": 0, "y": 0},
    {"x": 20, "y": 0},
    {"x": 20, "y": 15},
    {"x": 0, "y": 15}
  ]
}

# Generate design
POST /api/v1/design/generate
{
  "plot": {
    "coordinates": [...]
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
  "latitude": 28.6
}
```

## 🧮 Mathematical Formulas

### Polygon Area (Shoelace Theorem)

```
A = ½|Σᵢ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)|
```

### Bearing Capacity (Terzaghi)

```
qu = cNcSc + qNqSq + 0.5γBNγSγ
```

where:
- Nc, Nq, Nγ = bearing capacity factors
- c = soil cohesion
- q = surcharge
- γ = unit weight
- B = foundation width

### Beam Deflection

```
δ_max = 5wL⁴/(384EI)
```

## 🏗️ Project Structure

```
archai/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── domains/       # Domain engines
│   │   │   ├── geometry/  # Geometry calculations
│   │   │   ├── soil/      # Soil analysis
│   │   │   ├── structural/# Structural solver
│   │   │   ├── layout/    # Layout optimizer
│   │   │   └── optimization/ # AI optimization
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # State management
│   │   └── types/         # TypeScript types
│   └── package.json
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── docs/
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.