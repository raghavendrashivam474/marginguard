# MarginGuard

**AI-assisted financial leakage detection and investigation platform for SMEs, distributors and wholesalers.**

MarginGuard analyses purchase orders, supplier invoices and payment records to identify duplicate invoices, duplicate payments, invoice-payment mismatches, price discrepancies and other potential financial inconsistencies. It quantifies potential financial exposure and provides evidence-backed findings for human investigation.

---

## Current Development Status

> **Phase 0 — Project Foundation (MG-S0.1)**
>
> The repository is being initialized. No financial intelligence functionality exists yet. The frontend displays a minimal application shell and the backend exposes health-check endpoints.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite |
| Styling | Tailwind CSS |
| UI Components | shadcn/ui |
| Backend | Python + FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy 2 |
| Database | PostgreSQL |
| Migrations | Alembic |
| API | REST + OpenAPI |
| Containerization | Docker |

---

## Repository Overview
MarginGuard/
├── apps/
│ ├── web/ # React frontend
│ └── api/ # FastAPI backend
├── packages/ # Shared internal packages (future)
├── contracts/ # API & data schemas
├── data/ # Datasets (synthetic, public, fixtures)
├── docs/ # Architecture, engineering, API docs
├── scripts/ # Dev & maintenance utilities
└── tests/ # Cross-application tests

text


---

## Prerequisites

| Tool | Minimum Version | Check Command |
|---|---|---|
| Git | 2.30+ | `git --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Python | 3.11+ | `python --version` |

---

## Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

>>The development server starts at http://localhost:5173 by default.

## Backend Setup

```Bash
cd apps/api

# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your local values

# Start the server
uvicorn app.main:app --reload
```

>>The API starts at http://localhost:8000 by default.

## Environment Configuration

### Backend (apps/api/.env)

>Copy apps/api/.env.example to apps/api/.env and fill in your values:

```env
APP_NAME=MarginGuard
APP_ENV=development
APP_VERSION=0.1.0
DATABASE_URL=
LOG_LEVEL=INFO
```

### Frontend

>Vite uses VITE_-prefixed variables. Create apps/web/.env.local if needed:

```env
VITE_API_BASE_URL=http://localhost:8000
```

>Never commit .env or .env.local files. Only .env.example is tracked.

## Health Verification

Once both applications are running:

### Backend

```Bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

### Expected response:

```JSON
{
  "status": "healthy",
  "service": "marginguard-api",
  "version": "0.1.0"
}
```

### OpenAPI Documentation

Open http://localhost:8000/docs in your browser.

### Frontend
Open http://localhost:5173 — you should see the MarginGuard foundation screen.

## Documentation

- Repository Inspection Report
- Development Setup Guide
- Git Workflow
- System Overview

## License

See LICENSE.
