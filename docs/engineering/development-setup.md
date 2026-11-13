# Development Setup Guide

**Project:** MarginGuard  
**Sprint:** MG-S0.1  
**Last Updated:** 2025-07-11  

---

## Prerequisites

| Tool | Minimum Version | Recommended | Verify |
| :--- | :--- | :--- | :--- |
| Git | 2.30+ | Latest | `git --version` |
| Node.js | 18+ | 20 LTS or 24 | `node --version` |
| npm | 9+ | 10+ | `npm --version` |
| Python | 3.11+ | 3.12 or 3.13 | `python --version` |

> **Note:** Python 3.13 works, but some C-extension packages may lack pre-built wheels. If you encounter build errors, fall back to Python 3.12.

---

## Repository Structure

```text
MarginGuard/
├── apps/
│   ├── web/          # React + TypeScript + Vite frontend
│   └── api/          # FastAPI + Python backend
├── packages/         # Shared internal packages (future)
├── contracts/        # API & data schemas
├── data/             # Datasets (synthetic, public, fixtures)
├── docs/             # Documentation
├── scripts/          # Development utilities
└── tests/            # Cross-application tests

```

---

## Frontend Setup

### 1. Navigate to the frontend directory

```bash
cd apps/web

```

### 2. Install dependencies

```bash
npm install

```

### 3. Start the development server

```bash
npm run dev

```

The application will be available at `http://localhost:5173`.

### 4. Production build

```bash
npm run build

```

Output is written to `apps/web/dist/`.

### Key Configuration Files

| File | Purpose |
| --- | --- |
| `vite.config.ts` | Vite build config, Tailwind plugin, path aliases |
| `tsconfig.json` | TypeScript project references |
| `tsconfig.app.json` | TypeScript compiler options for application code |
| `components.json` | shadcn/ui component configuration |

### Path Aliases

The `@` alias maps to `apps/web/src/`:

```typescript
import { Button } from "@/components/ui/button"
// resolves to apps/web/src/components/ui/button

```

---

## Backend Setup

### 1. Navigate to the backend directory

```bash
cd apps/api

```

### 2. Create a virtual environment

```bash
python -m venv .venv

```

### 3. Activate the virtual environment

* **Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1

```


* **Windows (CMD):**
```cmd
.venv\Scripts\activate.bat

```


* **macOS / Linux:**
```bash
source .venv/bin/activate

```



### 4. Install dependencies

```bash
pip install -e ".[dev]"

```

This installs:

* **Runtime:** FastAPI, uvicorn, Pydantic, pydantic-settings, SQLAlchemy, Alembic
* **Development:** pytest, httpx, ruff

### 5. Configure environment variables

```bash
cp .env.example .env

```

Edit `.env` with your local values:

```env
APP_NAME=MarginGuard
APP_ENV=development
APP_VERSION=0.1.0
DATABASE_URL=
LOG_LEVEL=INFO

```

### 6. Start the development server

```bash
uvicorn app.main:app --reload

```

The API will be available at `http://localhost:8000`.

### 7. Verify health endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

```

Expected response:

```json
{
  "status": "healthy",
  "service": "marginguard-api",
  "version": "0.1.0"
}

```

### 8. OpenAPI documentation

Open `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc).

### Key Configuration Files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `.env.example` | Environment variable template |
| `app/core/config.py` | Pydantic Settings configuration class |
| `app/main.py` | FastAPI application entry point |

---

## Running Both Applications

Open two terminal windows:

* **Terminal 1 — Backend:**
```bash
cd apps/api
.venv\Scripts\Activate.ps1   # Windows
uvicorn app.main:app --reload

```


* **Terminal 2 — Frontend:**
```bash
cd apps/web
npm run dev

```



---

## Troubleshooting

### Python: `TOMLDecodeError` on `pyproject.toml`

* **Cause:** File was saved with a UTF-8 BOM (Byte Order Mark).
* **Fix:** Re-save the file as UTF-8 without BOM. In VS Code, click the encoding indicator in the status bar and choose **Save with Encoding > UTF-8**.

### Python: "Multiple top-level packages discovered"

* **Cause:** `setuptools` found `app/`, `migrations/`, and `tests/` as competing packages.
* **Fix:** Already resolved in `pyproject.toml` via `[tool.setuptools.packages.find] include = ["app*"]`.

### Frontend: "Cannot find module `@/...`"

* **Cause:** Path alias not configured.
* **Fix:** Ensure `tsconfig.app.json` contains:
```json
"baseUrl": ".",
"paths": { "@/*": ["./src/*"] }

```



### PowerShell: Execution policy blocks venv activation

* **Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

```



```