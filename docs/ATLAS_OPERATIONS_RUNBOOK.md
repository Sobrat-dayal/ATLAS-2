# ATLAS — Operations Runbook & Incident Management

**Audience:** Site Reliability Engineers (SRE), Platform Engineers, System Administrators  
**System:** ATLAS Financial Intelligence Platform  

---

## 1. Monitoring & Observability

### 1.1 Core Health Endpoints
- **Liveness & Health Probe:** `GET /api/v1/system/health`
  - Returns overall status (`HEALTHY`, `DEGRADED`, `UNHEALTHY`) and sub-checks for PostgreSQL, Redis, AI Gateway, NautilusTrader, Brokers, and Data Pipelines.
- **Readiness & Gate Status:** `GET /api/v1/system/readiness`
  - Returns launch verdict, gate evaluations (Gates A–J), blockers, and signatory sign-off.
- **Performance Benchmarks:** `GET /api/v1/system/benchmarks`
  - Reports p50, p95, p99 latencies and throughput against SLO thresholds.

### 1.2 Key Alert Thresholds
| Metric | Warning Threshold | Critical Threshold | Action |
| :--- | :--- | :--- | :--- |
| **API Latency (p95)** | > 100 ms | > 250 ms | Check Redis cache hit rate & DB connection pool |
| **Error Rate (5xx)** | > 0.5% | > 2.0% | Inspect Uvicorn error logs, check DB saturation |
| **Memory Utilization** | > 75% | > 90% | Scale out container replicas |
| **Active Kill Switches**| >= 1 | >= 5 | Check paper trading risk breaches |

---

## 2. Emergency Operational Procedures

### 2.1 Activating Emergency Kill Switch (Account Level)
If an algorithm or paper trading agent malfunctions:
```bash
POST /api/v1/trading/paper/accounts/{account_id}/kill-switch
Content-Type: application/json

{
  "reason": "Emergency risk limit violation"
}
```
*Effect:* Instantly freezes new order submissions on the specified account. Existing open orders are cancelled.

### 2.2 Global Service Drain & Maintenance Mode
To perform zero-downtime maintenance:
1. Shift traffic away from target instance cluster in load balancer.
2. Allow active WebSocket connections and worker tasks to drain gracefully (`SIGTERM` initiates a 30s drain timeout).
3. Apply database migrations via Alembic.
4. Restore cluster to active pool.

---

## 3. Database Maintenance & Migration Runbook

1. **Pre-Migration Backup:** Verify WAL archive status.
2. **Execute Migrations:** Run `uv run alembic upgrade head` in staging first.
3. **Rollback Plan:** In the event of schema incompatibility, run `uv run alembic downgrade -1`.
