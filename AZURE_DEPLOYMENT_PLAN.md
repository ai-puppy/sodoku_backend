# Azure App Service Deployment Plan for Sudoku Web App

## Overview
Deploy your full-stack Sudoku application (React/Vite frontend + FastAPI backend) to Azure App Service with proper production configuration.

## Phase 1: Prerequisites & Setup (30 minutes)
1. **Azure Account Setup**
   - Create Azure account (free tier available)
   - Install Azure CLI locally
   - Login via `az login`

2. **Project Preparation**
   - Add production configuration files
   - Configure environment variables
   - Set up build scripts

## Phase 2: Backend Deployment (45 minutes)
1. **Prepare FastAPI for Production**
   - Create `requirements.txt` from `pyproject.toml`
   - Add startup command configuration
   - Configure database connection for Azure PostgreSQL
   - Set up environment variables

2. **Deploy Backend to Azure App Service**
   - Create App Service for Python runtime
   - Configure startup command: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app`
   - Deploy code via Azure CLI
   - Set up Azure PostgreSQL database
   - Configure connection strings

## Phase 3: Frontend Deployment (30 minutes)
1. **Prepare React/Vite for Production**
   - Configure API base URL for production
   - Build production bundle
   - Create static file serving configuration

2. **Deploy Frontend Options (Choose One)**
   - **Option A**: Azure Static Web Apps (simpler, static hosting)
   - **Option B**: Azure App Service with Node.js (more control)

## Phase 4: Integration & Configuration (30 minutes)
1. **Configure CORS**
   - Set frontend domain in backend CORS settings
   - Test cross-origin requests

2. **Environment Configuration**
   - Set production environment variables
   - Configure JWT secrets
   - Set up SSL certificates

## Phase 5: Testing & Optimization (30 minutes)
1. **End-to-End Testing**
   - Test user registration/login
   - Test game creation and gameplay
   - Verify database operations

2. **Performance & Monitoring**
   - Configure logging
   - Set up application insights
   - Test performance under load

## Estimated Total Time: 2.5-3 hours
## Learning Outcomes:
- Azure App Service deployment
- Production configuration management
- Database setup in cloud
- CORS and security configuration
- CI/CD pipeline basics

## Detailed Steps

### Backend Deployment Details

#### 1. Create requirements.txt
```bash
# Extract dependencies from pyproject.toml
uv export --format requirements-txt --output-file requirements.txt
```

#### 2. Startup Command for Azure App Service
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

#### 3. Azure CLI Commands
```bash
# Create resource group
az group create --name sudoku-rg --location "East US"

# Create App Service plan
az appservice plan create --name sudoku-plan --resource-group sudoku-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group sudoku-rg --plan sudoku-plan --name sudoku-backend --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set --resource-group sudoku-rg --name sudoku-backend --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app"

# Deploy code
az webapp up --name sudoku-backend --resource-group sudoku-rg
```

### Frontend Deployment Details

#### Option A: Azure Static Web Apps
```bash
# Build the frontend
npm run build

# Deploy using Azure CLI
az staticwebapp create --name sudoku-frontend --resource-group sudoku-rg --source https://github.com/yourusername/sudoku_frontend --branch main --app-location "/" --output-location "dist"
```

#### Option B: Azure App Service (Node.js)
```bash
# Create web app for frontend
az webapp create --resource-group sudoku-rg --plan sudoku-plan --name sudoku-frontend --runtime "NODE:18-lts"

# Configure startup command for serving static files
az webapp config set --resource-group sudoku-rg --name sudoku-frontend --startup-file "pm2 serve dist --no-daemon --spa"
```

### Environment Variables Setup
```bash
# Backend environment variables
az webapp config appsettings set --resource-group sudoku-rg --name sudoku-backend --settings DATABASE_URL="postgresql://..." SECRET_KEY="your-secret-key" ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Frontend environment variables (if using App Service)
az webapp config appsettings set --resource-group sudoku-rg --name sudoku-frontend --settings VITE_API_URL="https://sudoku-backend.azurewebsites.net"
```

### Database Setup
```bash
# Create PostgreSQL server
az postgres server create --resource-group sudoku-rg --name sudoku-db-server --location "East US" --admin-user sudokuadmin --admin-password "YourPassword123!" --sku-name B_Gen5_1

# Create database
az postgres db create --resource-group sudoku-rg --server-name sudoku-db-server --name sudokudb

# Configure firewall rule for Azure services
az postgres server firewall-rule create --resource-group sudoku-rg --server sudoku-db-server --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

### CORS Configuration
Add to your FastAPI main.py:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sudoku-frontend.azurewebsites.net"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing Checklist
- [ ] Backend health check: `https://sudoku-backend.azurewebsites.net/health`
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Game creation works
- [ ] Game state persistence works
- [ ] API calls from frontend to backend work
- [ ] Database operations work correctly

### Troubleshooting
- Check application logs: `az webapp log tail --name sudoku-backend --resource-group sudoku-rg`
- Monitor performance: Enable Application Insights in Azure portal
- Test locally first: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`
