# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based Sudoku game backend with user authentication and game state management. The project uses SQLAlchemy for database operations, Alembic for migrations, and includes a complete Sudoku puzzle generator and validator.

## Development Setup

### Package Management
This project uses `uv` as the Python package manager. Key commands:
- `uv sync` - Install/sync dependencies from pyproject.toml
- `uv run <command>` - Run commands in the project environment
- `uv add <package>` - Add new dependencies
- `uv remove <package>` - Remove dependencies

### Database Setup
- Database: PostgreSQL (configurable via DATABASE_URL)
- Migrations: Alembic
- Setup commands:
  ```bash
  # Install dependencies
  uv sync

  # Run database migrations
  uv run alembic upgrade head

  # Create new migration (after model changes)
  uv run alembic revision --autogenerate -m "description"
  ```

### Running the Application
```bash
# Development server with auto-reload
python main.py

# Or using uv
uv run python main.py

# Direct uvicorn
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Architecture

### Core Components

**FastAPI Application** (`app/main.py`)
- Main FastAPI app with CORS middleware
- Health check endpoint at `/health`
- API routers for auth and games

**Database Layer** (`app/database.py`)
- SQLAlchemy engine and session management
- Base declarative class for models
- Dependency injection for database sessions

**Authentication** (`app/core/security.py`, `app/api/auth.py`)
- JWT-based authentication using python-jose
- Password hashing with passlib and bcrypt
- User registration and login endpoints

**Game Engine** (`app/core/sudoku.py`)
- Complete Sudoku puzzle generator with configurable difficulty
- Puzzle validation and solving algorithms
- Board serialization/deserialization utilities

**Models** (`app/models/`)
- `User`: User accounts with password hashing
- `Game`: Game instances with puzzle data, current state, and completion tracking

**API Endpoints** (`app/api/`)
- `/auth`: User registration, login, token management
- `/games`: CRUD operations for Sudoku games, game state updates

### Database Schema

**Users Table**
- Authentication and user profile data
- One-to-many relationship with games

**Games Table**
- Stores initial puzzle, solution, and current state as JSON
- Tracks difficulty level, completion status, and timestamps
- Foreign key relationship to users

### Configuration

**Settings** (`app/config.py`)
- Uses pydantic-settings for environment-based configuration
- Key settings: DATABASE_URL, SECRET_KEY, token expiration
- Environment variables loaded from `.env` file

**Environment Setup**
- Copy `.env.example` to `.env` and configure:
  - `DATABASE_URL`: PostgreSQL connection string
  - `SECRET_KEY`: JWT signing key (change in production)
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Game Logic

The Sudoku engine supports four difficulty levels:
- Easy: 35 cells removed
- Medium: 45 cells removed
- Hard: 55 cells removed
- Expert: 65 cells removed

Game progression automatically suggests difficulty based on completed games (every 5 completions advances difficulty).

## Database Migrations

Alembic is configured and ready to use:
- Configuration in `alembic.ini`
- Migration scripts in `alembic/versions/`
- Run `uv run alembic upgrade head` after pulling changes
- Generate migrations with `uv run alembic revision --autogenerate -m "description"`

## Testing

This project includes comprehensive unit tests with high coverage requirements.

### Running Tests

```bash
# Run all tests (parallel execution by default)
uv run pytest

# Run with coverage report (parallel)
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_core/          # Core functionality tests
uv run pytest tests/test_api/           # API endpoint tests
uv run pytest tests/test_models/        # Database model tests
uv run pytest tests/test_schemas/       # Pydantic schema tests

# Run specific test file
uv run pytest tests/test_core/test_sudoku.py -v

# Parallel execution options
uv run pytest -n auto                   # Auto-detect CPU cores
uv run pytest -n 4                      # Use 4 parallel workers
uv run pytest -n 0                      # Disable parallel execution

# Run tests with coverage threshold (configured to require 90%+)
uv run pytest --cov-fail-under=90

# Use the convenient test runner script
python test.py all                      # All tests with coverage (parallel)
python test.py quick                    # Fast run without coverage (parallel)
python test.py sequential               # Sequential execution (for debugging)
python test.py coverage                 # Comprehensive coverage report
```

### Test Configuration

- **pytest.ini**: Test configuration and coverage settings with parallel execution
- **conftest.py**: Shared fixtures for database, authentication, and test data
- **Coverage requirement**: 90% minimum coverage
- **Test database**: Uses SQLite in-memory database for isolation
- **Parallel execution**: Automatically uses all CPU cores with pytest-xdist

### Test Structure

Tests are organized by functionality:
- **Core tests**: Business logic (Sudoku engine, security functions)
- **API tests**: Endpoint behavior, authentication, validation
- **Model tests**: Database operations, relationships, constraints
- **Schema tests**: Pydantic validation and serialization

## API Documentation

The FastAPI automatic documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


frontend code path: /Users/hw/Desktop/sodoku_frontend
