# 🐳 Docker Setup for AgentHub

## Quick Start

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Option 1: Use the start script (recommended)
```bash
./start-docker.sh
```

### Option 2: Manual commands
```bash
# 1. Copy and edit environment variables
cp .env.example .env
# Edit .env and add your API keys

# 2. Build and start containers
docker-compose up --build -d

# 3. View logs
docker-compose logs -f
```

## 🚀 Access the Application

Once running:
- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

## 📋 Useful Commands

### Start containers
```bash
docker-compose up -d
```

### Stop containers
```bash
docker-compose down
# or use the script:
./stop-docker.sh
```

### View logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuild containers
```bash
docker-compose up --build
```

### Restart a service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Check container status
```bash
docker-compose ps
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## 🔧 Configuration

### Environment Variables

Required in `.env`:
```bash
ANTHROPIC_API_KEY=your_key_here
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

### Ports

Default ports (change in `docker-compose.yml`):
- Frontend: `5173`
- Backend: `5000`

### Volumes

The following directories are mounted for hot-reload during development:
- Frontend: `./frontend/src`, `./frontend/public`
- Backend: `./agents`, `./orchestrator.py`, `./app.py`

## 🐛 Troubleshooting

### Port already in use
```bash
# Check what's using the port
lsof -i :5173  # or :5000

# Stop the process or change the port in docker-compose.yml
```

### Containers won't start
```bash
# Check logs
docker-compose logs

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Can't connect to backend from frontend
```bash
# Make sure both containers are on the same network
docker network ls
docker network inspect agenthub-network
```

### Changes not reflected
```bash
# Rebuild with no cache
docker-compose build --no-cache
docker-compose up
```

## 📊 Production Deployment

For production, create a separate `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    environment:
      - FLASK_ENV=production
    restart: always

  frontend:
    build:
      context: ./frontend
      target: production
    restart: always
```

Then run:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🧹 Cleanup

Remove all containers and volumes:
```bash
docker-compose down -v
```

Remove images:
```bash
docker rmi agenthub-backend agenthub-frontend
```
