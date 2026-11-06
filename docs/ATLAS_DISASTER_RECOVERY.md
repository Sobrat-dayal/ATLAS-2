# ATLAS — Disaster Recovery & Business Continuity Plan

**Classification:** Infrastructure Resilience & DR Runbook  
**Target Recovery Point Objective (RPO):** < 15 minutes  
**Target Recovery Time Objective (RTO):** < 30 minutes  
**Verification Drill Status:** PASSED (Staging Drill Executed & Verified)  

---

## 1. Resilience Architecture

ATLAS maintains high availability and disaster resilience across all data layers:
1. **Primary Relational Store (PostgreSQL):** Multi-AZ replication with automated daily full snapshots and continuous write-ahead log (WAL) archiving for Point-In-Time Recovery (PITR).
2. **Analytical Store (ClickHouse):** Clustered replica pairs with distributed tables.
3. **In-Memory Cache (Redis/Valkey):** Redis AOF (Append-Only File) enabled with multi-AZ failover.
4. **Application Statelesness:** API and web tiers are 100% stateless; state is preserved in persistent stores or event logs.

---

## 2. Backup Strategy

| Component | Backup Type | Frequency | Retention | Encryption |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | Continuous WAL + Full Snapshot | Continuous + Daily | 30 Days | AES-256 |
| **ClickHouse** | Disk Snapshot | Weekly | 90 Days | AES-256 |
| **Event Store** | Parquet Export | Daily | 365 Days | AES-256 |
| **Secrets / Config** | Encrypted Vault Backup | On-Change | 1 Year | KMS Encrypted |

---

## 3. Disaster Recovery Drill Procedure (Staging)

### Step 1: Triggering Simulated Drill
Drills are executed periodically using the Production Hardening Service:
```bash
POST /api/v1/system/dr-drill
Content-Type: application/json

{
  "target_environment": "STAGING"
}
```

> [!CAUTION]
> Production environment drills are categorically blocked (`target_environment != "PRODUCTION"`). Replay side-effects to external systems are strictly suppressed during all restore drills.

### Step 2: Verification Checklist
During the drill, the system automatically verifies:
1. Snapshot archive decryption and extraction.
2. Relational schema reconstruction and table population.
3. Record count and integrity checksum match against origin state.
4. Suppressed outbound event delivery (zero external webhooks or simulated orders dispatched during replay).

---

## 4. Emergency Failover Procedure (Production Outage)

In the event of a total primary region outage:
1. **DNS Cutover:** Route53 / Cloudflare DNS updated to point `app.atlas.quant.io` and `api.atlas.quant.io` to secondary region load balancers.
2. **Database Promotion:** Promote secondary PostgreSQL read replica to primary read-write.
3. **Verify Integrity:** Run `/api/v1/system/health` to confirm all 6 core probes report `HEALTHY`.
4. **Notify Stakeholders:** Update ATLAS status page with incident resolution details.
