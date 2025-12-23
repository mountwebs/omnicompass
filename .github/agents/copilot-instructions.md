# omnicompass Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-23

## Active Technologies

- Python 3.10+ (Backend, Conda "astro" env), Node.js 18+ (Frontend) (001-core-architecture)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.10+ (Backend, Conda "astro" env), Node.js 18+ (Frontend): Follow standard conventions

## Recent Changes

- 001-core-architecture: Added Python 3.10+ (Backend, Conda "astro" env), Node.js 18+ (Frontend)

<!-- MANUAL ADDITIONS START -->
## Environment & Startup
- **Backend**: Always activate the `astro` conda environment. Run from the `backend` directory using the module syntax.
  ```bash
  conda activate astro
  cd backend
  python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
  ```
<!-- MANUAL ADDITIONS END -->
