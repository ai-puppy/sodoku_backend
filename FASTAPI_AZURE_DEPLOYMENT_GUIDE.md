# Deploy FastAPI Backend with PostgreSQL to Azure App Service

## Phase 1: Prepare Your Backend for Production (15 minutes)

### 1.1 Create requirements.txt from pyproject.toml
```bash
uv export --format requirements-txt --output-file requirements.txt
```

### 1.2 Create startup script (startup.sh)
- Script to run Alembic migrations before starting FastAPI
- Configure proper Gunicorn workers for production

### 1.3 Update configuration for Azure environment
- Modify config.py to read Azure connection strings
- Update alembic/env.py to use environment variables

### 1.4 Update CORS settings
- Add your frontend URL to allowed origins in main.py

## Phase 2: Create Azure PostgreSQL Database (20 minutes)

### 2.1 Create PostgreSQL Flexible Server via Azure Portal or CLI
```bash
az postgres flexible-server create \
  --resource-group sudoku-rg \
  --name sudoku-postgres-server \
  --location "East US" \
  --admin-user sudokuadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32 \
  --version 15
```

### 2.2 Create database
```bash
az postgres flexible-server db create \
  --resource-group sudoku-rg \
  --server-name sudoku-postgres-server \
  --database-name sudokudb
```

### 2.3 Configure firewall for Azure services
```bash
az postgres flexible-server firewall-rule create \
  --resource-group sudoku-rg \
  --name sudoku-postgres-server \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

## Phase 3: Deploy FastAPI to Azure App Service (25 minutes)

### 3.1 Create App Service
```bash
az webapp create \
  --resource-group sudoku-rg \
  --plan sudoku-plan \
  --name sudoku-backend-api \
  --runtime "PYTHON:3.11" \
  --startup-file "startup.sh"
```

### 3.2 Configure environment variables
```bash
# Get connection string from PostgreSQL
CONNECTION_STRING="postgresql://sudokuadmin:YourSecurePassword123!@sudoku-postgres-server.postgres.database.azure.com:5432/sudokudb?sslmode=require"

# Set environment variables
az webapp config appsettings set \
  --resource-group sudoku-rg \
  --name sudoku-backend-api \
  --settings \
    DATABASE_URL="$CONNECTION_STRING" \
    SECRET_KEY="your-production-secret-key-generate-secure-one" \
    ACCESS_TOKEN_EXPIRE_MINUTES="30" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### 3.3 Deploy code
```bash
# Zip your application
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x ".env" -x ".git/*" -x "venv/*" -x ".venv/*"

# Deploy
az webapp deployment source config-zip \
  --resource-group sudoku-rg \
  --name sudoku-backend-api \
  --src deploy.zip
```

## Phase 4: Run Database Migrations (10 minutes)

### 4.1 SSH into App Service
- Go to Azure Portal > Your App Service > SSH
- Or use: `az webapp ssh --resource-group sudoku-rg --name sudoku-backend-api`

### 4.2 Run migrations
```bash
cd /home/site/wwwroot
alembic upgrade head
python app/core/seed_data.py  # If you have initial data
```

## Phase 5: Test and Verify (10 minutes)

### 5.1 Check health endpoint
```bash
curl https://sudoku-backend-api.azurewebsites.net/health
```

### 5.2 Test API documentation
- Visit: https://sudoku-backend-api.azurewebsites.net/docs

### 5.3 Update frontend API URL
- Update your frontend to point to: https://sudoku-backend-api.azurewebsites.net

### 5.4 Monitor logs
```bash
az webapp log tail \
  --resource-group sudoku-rg \
  --name sudoku-backend-api
```

## Files to Create/Modify:

### startup.sh
```bash
#!/bin/bash
alembic upgrade head
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

### Updated config.py for Azure
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/sudoku_db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    model_config = {"env_file": ".env"}
```

### Updated CORS in main.py
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.azurestaticapps.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Alternative: Using Azure Developer CLI (Quick Deploy)

If you prefer a faster automated approach:

### Prerequisites
```bash
# Install Azure Developer CLI
# On macOS: brew install azure-dev
# On Windows: winget install microsoft.azd
# On Linux: curl -fsSL https://aka.ms/install-azd.sh | bash

# Login
azd auth login
```

### Quick Deploy Steps
```bash
# Clone Microsoft's sample template (to understand structure)
git clone https://github.com/Azure-Samples/msdocs-fastapi-postgresql-sample-app.git sample

# Adapt your code to match the template structure
# Key files needed:
# - azure.yaml (defines services)
# - infra/ directory (ARM templates)
# - requirements.txt

# Initialize and deploy
azd init --template your-repo-url
azd up
```

## Detailed Troubleshooting

### Common Issues and Solutions

#### 1. Migration Errors
```bash
# Check database connectivity
psql "postgresql://sudokuadmin:password@sudoku-postgres-server.postgres.database.azure.com:5432/sudokudb?sslmode=require"

# Verify alembic configuration
alembic current
alembic history
```

#### 2. App Service Startup Issues
```bash
# Check startup logs
az webapp log tail --name sudoku-backend-api --resource-group sudoku-rg

# Test startup command locally
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

#### 3. Database Connection Issues
- Verify firewall rules allow Azure services
- Check connection string format
- Ensure PostgreSQL server allows connections
- Verify SSL mode is set correctly

#### 4. Environment Variables
```bash
# List all app settings
az webapp config appsettings list --name sudoku-backend-api --resource-group sudoku-rg

# Update specific setting
az webapp config appsettings set --name sudoku-backend-api --resource-group sudoku-rg --settings KEY="value"
```

## Security Considerations

### 1. Connection Security
- Always use SSL connections (`sslmode=require`)
- Use strong passwords for database
- Consider using managed identity for authentication

### 2. Environment Variables
- Never commit secrets to source control
- Use Azure Key Vault for sensitive data in production
- Rotate secrets regularly

### 3. Network Security
- Configure PostgreSQL firewall rules restrictively
- Consider using VNet integration for private networking
- Enable Azure App Service authentication if needed

## Performance Optimization

### 1. Database Connection Pooling
```python
# In your database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 2. App Service Scaling
```bash
# Scale up (more powerful instance)
az appservice plan update --name sudoku-plan --resource-group sudoku-rg --sku S1

# Scale out (more instances)
az webapp config set --name sudoku-backend-api --resource-group sudoku-rg --auto-heal-enabled true
```

### 3. Monitoring
- Enable Application Insights
- Set up health checks
- Monitor database performance metrics
- Configure alerts for errors and performance issues

## Total Time: ~1.5 hours

## Success Checklist
- [ ] PostgreSQL database created and accessible
- [ ] App Service created with correct runtime
- [ ] Environment variables configured
- [ ] Code deployed successfully
- [ ] Database migrations completed
- [ ] Health endpoint returns 200
- [ ] API documentation accessible
- [ ] Frontend can connect to backend
- [ ] Authentication working
- [ ] Game functionality working end-to-end
