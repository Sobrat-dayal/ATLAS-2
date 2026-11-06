# ATLAS Privacy Policy

**Effective Date:** 2026-11-06  
**Platform:** ATLAS — AI-Native Financial Intelligence and Quantitative Research Operating System  

---

## 1. Introduction

ATLAS ("we", "our", or "the Platform") respects your privacy and is committed to protecting your personal data and proprietary financial research. This Privacy Policy explains how we collect, store, process, and protect your information when you use the ATLAS application, APIs, and associated services.

---

## 2. Information We Collect

1. **Account & Identity Data:** When registering an account, we collect authentication identifiers (e.g., email address, user ID, tenant ID) managed securely via Supabase Auth.
2. **Quantitative Research & Workspace Data:** We store user-created workspaces, watchlists, screeners, backtests, and research notes. This data is strictly tenant-scoped and isolated using database Row-Level Security (RLS).
3. **Simulated Paper Trading & Sandbox Data:** Virtual paper trading orders, positions, and simulated account balances are stored solely for research and simulation purposes. No real bank accounts or payment credentials are required or stored.
4. **Autonomous Agent & Workflow Data:** Agent graph definitions, custom tool scripts, and execution transcripts are stored in tenant-isolated schemas. We do not use your proprietary prompts or quantitative strategies to train foundational AI models.
5. **Operational Telemetry:** We collect anonymized diagnostic telemetry, latency benchmarks, and error rates to monitor platform performance and system health.

---

## 3. How We Use Information

- To provide, maintain, and optimize platform services.
- To enforce multi-tenant security boundaries and access permissions.
- To execute sandboxed simulations, backtests, and autonomous workflows.
- To detect, prevent, and remediate security vulnerabilities or unauthorized access.

---

## 4. Multi-Tenant Isolation & Data Ownership

- **Strict Isolation:** All customer data is segregated by tenant identifier. No tenant may view, query, or infer another tenant's quantitative models or portfolios.
- **Data Ownership:** You retain full and exclusive intellectual property rights to your research, models, strategies, and agent configurations.
- **Zero Live Trading:** ATLAS does not process live brokerage orders or real-money financial transactions.

---

## 5. Security Safeguards

We implement institutional-grade security safeguards:
- Encryption in transit (TLS 1.3) and encryption at rest (AES-256).
- Cryptographic secret vaulting for sandbox API tokens using Fernet encryption.
- Continuous vulnerability scanning, SSRF defense, and supply-chain package verification.

---

## 6. Contact & Rights

Users have the right to inspect, export, or delete their personal account data at any time through platform settings or by contacting the ATLAS Security & Privacy Officer.
