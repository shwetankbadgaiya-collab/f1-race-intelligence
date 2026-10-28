# F1 RACE INTELLIGENCE — Interactive Motorsport Analytics Dashboard (2010–2026)

> **Enterprise-grade Formula 1 analytics, telemetry insights, championship progression, and reliability intelligence.**

![F1 Race Intelligence Banner](https://raw.githubusercontent.com/f1-race-intelligence/assets/main/banner.png)

---

## 🏆 Project Overview

**F1 Race Intelligence** is a professional, high-performance web-based analytics platform designed for F1 team performance strategists, motorsport broadcast analysts, FIA technical regulation analysts, motorsport journalists, and data analytics researchers.

The platform transforms raw historical race telemetry from **2010 through 2026** into deterministic visual insights, multi-team comparisons, driver head-to-head metrics, circuit failure rates, and granular data exploration tools.

### Key Highlights
- **Strict Data Integrity**: Adheres to strict anti-fabrication guidelines. Unrecorded tyre stint telemetry is explicitly reported as unavailable rather than simulating fake compound degradation curves.
- **100% Real Database Queries**: 299 Grands Prix, 42 drivers, 22 constructors, 34 circuits, and 5,945 classified & unclassified race results computed directly from normalized SQLite/PostgreSQL schemas.
- **Automated Insights Engine**: Deterministic statistical observations generated on-the-fly comparing year-over-year constructor trajectories, driver podium conversion rates, and circuit retirement spikes.
- **Premium Motorsport Design**: Dark motorsport aesthetic (`#0F0F0F` charcoal, `#E10600` racing red accent, clean typography, responsive charts, and fluid transitions).

---

## 🧭 Dashboard Architecture & Sections

The application features 9 dedicated analytical views:

1. **Overview Dashboard** (`/`)
   - 6 Live KPI Cards (Grands Prix, Drivers, Constructors, Circuits, Podiums, Finish Rate).
   - Multi-constructor championship trajectory line chart (Red Bull Racing, Mercedes, Ferrari, McLaren).
   - Driver performance leaderboard.
   - Race completion donut chart (classified finishes vs retirements).
   - Podium distribution breakdown.
   - Automated insights notification bar.

2. **Driver Analytics** (`/drivers`)
   - Searchable driver master directory with instant profile cards.
   - Career starts, victories, podiums, pole positions, finish rate, and average finishing position.
   - Career finishing position histogram (P1–P20 and DNFs).
   - Interactive driver vs driver head-to-head comparison tool with statistical delta highlights.

3. **Constructor Analytics** (`/constructors`)
   - Multi-team championship trend analyzer with constructor visibility toggles.
   - Season-by-season championship position heatmap (P1 Gold, P2 Silver, P3 Bronze matrix).
   - Driver point contribution breakdown within teams.
   - Team-vs-team head-to-head comparison matrix.

4. **Tyre Strategy Analysis** (`/tyres`)
   - Strict adherence to Regulation §8 (Data Integrity Directive).
   - Transparent disclosure on stint-level telemetry requirements (Pirelli C1–C5 specifications).
   - Real pit stop duration metrics and technical architecture roadmap for FastF1 integration.

5. **Circuit Intelligence** (`/circuits`)
   - Top Grand Prix host country rankings.
   - Circuit participation leaderboard with GPS coordinates (lat, lng, altitude).
   - Circuit-level DNF rate comparisons and historical round lists.

6. **Reliability & DNF Analysis** (`/reliability`)
   - Annual DNF trends and completion percentages over time (2010–2024).
   - Categorized failure mode breakdown: Engine/Power Unit, Gearbox, Collision, Brakes, Electrical, Suspension.
   - Constructor reliability leaderboard ranked by race completion percentage.

7. **Global Podiums** (`/podiums`)
   - Comprehensive podium achievements by driver, constructor, and driver nationality.
   - P1 (Gold), P2 (Silver), P3 (Bronze) distribution charts.
   - Searchable driver podium directory with export capability.

8. **Data Explorer & Schema Audit** (`/data-explorer`)
   - Direct pagination, sorting, and full-text search across 9 relational tables.
   - Missing value inspection and completeness scores.
   - One-click CSV export for any selected dataset.
   - Interactive CSV file upload and schema validator.

9. **About Project** (`/about`)
   - Problem statement, objectives, target audiences, system architecture diagram, and methodology.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 with Vite & TypeScript
- **Styling**: Tailwind CSS with custom Formula 1 dark palette
- **Charts**: Recharts (ResponsiveContainer, LineChart, BarChart, PieChart)
- **Icons**: Lucide React
- **Motion**: Framer Motion
- **Tables**: TanStack React Table

### Backend
- **Framework**: Python 3.13, FastAPI (Async ASGI)
- **Data Science**: Pandas, NumPy
- **Validation**: Pydantic v2 schemas
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (production-ready for PostgreSQL)
- **Testing**: Pytest

---

## 🚀 Quick Start Guide

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ingest historical F1 data (populates data/f1_data.db and writes data/*.csv)
cd ..
python scripts/ingest_data.py

# Run the FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend interactive API documentation is available at: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

Open your browser to: **http://localhost:5173**

---

## 🧪 Running Automated Tests

Run the complete test suite verifying all 16 core analytical services and endpoints:

```bash
cd backend
pytest tests/test_f1_services.py -v
```

All 16 test suites pass with 100% assertions covering:
- Season range verification
- Overview metric calculations (299 races, 5,945 results)
- Championship trend aggregations
- Driver profiles and head-to-head calculations
- Constructor profiles and heatmap matrices
- Circuit GPS coordinates and DNF rates
- Failure mode categorization
- Data quality audits and CSV export streaming
- Deterministic insights generation

---

## 🌐 Production Deployment

### Docker Deployment
```bash
cd backend
docker build -t f1-race-intelligence .
docker run -p 8000:8000 f1-race-intelligence
```

### Vercel (Frontend)
The frontend includes a pre-configured `vercel.json` for client-side single-page routing:
```bash
cd frontend
vercel deploy
```

### Render (Full Stack)
The project root includes `render.yaml` defining both the Python FastAPI backend service and the static Vite frontend site with environment variable bindings.

---

## 📜 License & Acknowledgments

- **Data Attribution**: Ergast Motor Racing Database / Jolpica-F1 Project.
- **License**: MIT License.
- **Disclaimer**: Built for hackathon demonstration and educational motorsport research. Not affiliated with Formula 1 or the FIA.
