# ATLAS — Production Deployment Guide

**Target Environment:** Containerized Cloud Production (Kubernetes / ECS / Cloud Run)  
**System Architecture:** Next.js Frontend + Python FastAPI Backend + PostgreSQL + Redis + ClickHouse  

---

## 1. Prerequisites & Infrastructure Setup

### 1.1 Infrastructure Components
1. **Frontend Host:** Node.js 20+ runtime or containerized Next.js cluster.
2. **Backend API Host:** Python 3.12+ ASGI container cluster (FastAPI + Uvicorn).
3. **Primary Database:** PostgreSQL 16+ with PostGIS extension enabled (Supabase or AWS RDS / Cloud SQL).
4. **Timeseries Analytics:** ClickHouse Cloud or self-hosted ClickHouse cluster for high-throughput tick data.
5. **Cache & Messaging:** Redis 7+ or Valkey cluster for caching, rate limiting, and WebSocket pub/sub.
6. **Object Storage:** S3-compatible bucket for report artifacts and model snapshots.

---

## 2. Environment Variables Specification

### 2.1 Backend (`apps/api/.env`)
```bash
# Environment Mode
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security & CORS
SECRET_KEY=generate-secure-32-byte-hex-string
ALLOWED_ORIGINS=https://atlas.quant.io,https://app.atlas.quant.io

# Supabase Auth & PostgreSQL
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/atlas
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_KEY=[SERVICE_ROLE_KEY]
SUPABASE_JWT_SECRET=[JWT_SECRET]

# Redis / Valkey
REDIS_URL=rediss://default:[PASSWORD]@[HOST]:6379

# ClickHouse Timeseries
CLICKHOUSE_HOST=[HOST]
CLICKHOUSE_PORT=8443
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=[PASSWORD]
CLICKHOUSE_SECURE=true

# Financial Safety Firewall (STRICT ENFORCEMENT)
ATLAS_FINANCIAL_SAFETY_FIREWALL=true
PERMIT_LIVE_BROKER_EXECUTION=false
```

### 2.2 Frontend (`apps/web/.env.production`)
```bash
NEXT_PUBLIC_APP_URL=https://app.atlas.quant.io
NEXT_PUBLIC_API_URL=https://api.atlas.quant.io
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[ANON_KEY]
```

---

## 3. Build & Containerization

### 3.1 Backend Container
```dockerfile
# apps/api/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY src/ ./src
EXPOSE 8000
CMD ["uvicorn", "atlas_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3.2 Frontend Container
```dockerfile
# apps/web/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 4. Health Checks & Readiness Probes

### Kubernetes Probe Definitions
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/system/health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/system/readiness
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## 5. Deployment Verification Checklist

1. [x] In-memory SecretVault initialized with unique Fernet key.
2. [x] Financial Safety Firewall verified: live execution categorically blocked.
3. [x] All 51 Next.js routes built and statically prerendered or dynamic.
4. [x] Row-Level Security policies active across all tenant tables.
5. [x] Redis and PostgreSQL connections validated with TLS.
