# OpsAutopsy

**Cloud-agnostic, multi-cluster Kubernetes incident forensics engine**

OpsAutopsy reconstructs what happened during outages by correlating Kubernetes events, workload state, and change signals across clusters into clear, time-ordered incident reports.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.24+-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)

---

## The Problem

When incidents occur, your team scrambles to answer:

- **What happened first?** — Alert floods make root cause unclear
- **What changed?** — Deployments, configs, and infrastructure changes are scattered
- **Why did it fail?** — Correlation between events is lost in noise
- **How wide was the impact?** — Blast radius spans multiple clusters
- **Did this cascade?** — Cross-cluster failures are invisible

**Most observability tools show signals. OpsAutopsy explains incidents.**

---

## The Solution

OpsAutopsy is purpose-built for **post-incident analysis**, not real-time monitoring.

### Key Capabilities

**🔍 Multi-Cluster Incident Reconstruction**  
Correlate events across all your Kubernetes clusters in a single timeline

**🕐 Time-Travel Debugging**  
Query historical cluster state even after Kubernetes garbage-collects events

**🎯 Root Cause Classification**  
Automatically detect issue types: ImagePullBackOff, CrashLoop, OOMKilled, capacity constraints

**📊 Blast Radius Analysis**  
Understand incident scope: affected pods, deployments, namespaces, and clusters

**🔗 Change Correlation**  
Link incidents to deployments, config changes, and infrastructure events

**📝 Human-Readable Reports**  
Get clear incident narratives, not just raw data dumps

---

## Architecture

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Cluster A   │   │  Cluster B   │   │  Cluster C   │
│              │   │              │   │              │
│ OpsAutopsy   │   │ OpsAutopsy   │   │ OpsAutopsy   │
│ Agent        │   │ Agent        │   │ Agent        │
│ (DaemonSet)  │   │ (DaemonSet)  │   │ (DaemonSet)  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  ▼                  ▼
         ┌─────────────────────────────────┐
         │ Centralized PostgreSQL Database │
         │  (Events, State, Metadata)      │
         └────────────────┬────────────────┘
                          ▼
              ┌───────────────────────┐
              │ OpsAutopsy Analyzer   │
              │ (CLI - Stateless)     │
              └───────────────────────┘
```

---

## Components

### 1. OpsAutopsy Agent (Per-Cluster)

The agent runs inside each Kubernetes cluster as a **DaemonSet** and is responsible **only for collection**, never analysis.

#### What the Agent Does

- Watches the Kubernetes **Events API**
- Periodically captures **Pod, Deployment, and Node state**
- Normalizes timestamps to **UTC**
- Tags every record with a `cluster_id`
- Streams data to **centralized PostgreSQL database**

> **Why this matters:** Kubernetes events are ephemeral (≈1 hour TTL). The agent turns short-lived signals into durable incident history.

#### What the Agent Does NOT Do

- ❌ No alerting or notifications
- ❌ No remediation or auto-fixing
- ❌ No mutation of cluster state
- ❌ No network exposure or endpoints
- ❌ No analysis or correlation

**Design Principles:**
- **Read-only:** Zero risk to cluster stability
- **Lightweight:** Minimal resource footprint (~50MB RAM per node)
- **Safe:** No cluster state mutations, ever

### 2. Centralized Storage (PostgreSQL)

OpsAutopsy uses PostgreSQL as durable incident memory across all clusters.

**Why PostgreSQL?**
- Powerful time-series querying with native time-range indexes
- Native JSON support for flexible event payloads
- Cross-cluster correlation via SQL joins
- Battle-tested reliability and tooling
- Simple operational model (no specialized databases)

**Core Schema:**

```sql
-- events table
cluster_id, namespace, object_kind, object_name, 
reason, message, event_time

-- workload_state table
cluster_id, namespace, workload_name, workload_type,
status, restart_count, observed_time
```

Data retention can be managed with standard PostgreSQL partitioning or archived to object storage (S3/GCS) for long-term compliance.

### 3. OpsAutopsy Analyzer (CLI)

Stateless analysis engine that runs **outside your clusters** on your local machine or in CI/CD.

**Capabilities:**
- Query events across time windows and clusters
- Classify incident types automatically
- Calculate blast radius across namespaces and clusters
- Correlate changes with failures
- Generate human-readable incident reports
- Export structured data for integration

**Example Usage:**

```bash
# Analyze last 15 minutes across all clusters
opsautopsy analyze --last-minutes 15

# Analyze specific namespace in last hour
opsautopsy analyze --namespace payments --last-minutes 60

# Multi-cluster analysis with specific time
opsautopsy analyze --clusters prod-eu,prod-us --since 2026-01-15T16:00

# Export structured data
opsautopsy analyze --last-minutes 30 --format json > incident.json
```

### Separation: Agent vs Analyzer

| Component | Runs Where | Responsibility | State |
|-----------|-----------|----------------|-------|
| **Agent** | Inside Kubernetes | Collect & persist data | Stateless |
| **Analyzer** | Local machine / CI | Analyze & explain incidents | Stateless |

This separation enables:
- Safer cluster operations (agents are read-only)
- Easier upgrades (analyzer doesn't touch clusters)
- Offline analysis (query historical data anytime)
- Multi-cluster correlation (single analyzer, many clusters)

> **OpsAutopsy agents collect facts. OpsAutopsy CLI tells the story.**

---

## Sample Output

### Incident Summary

```
═══════════════════════════════════════════════════
INCIDENT ANALYSIS: 2024-01-15 18:14 - 18:32 UTC
═══════════════════════════════════════════════════

Detected Issues:
  • IMAGE_PULL_FAILURE (ErrImagePull, ImagePullBackOff)
  • CRASH_LOOP (CrashLoopBackOff)
  • CAPACITY_SCHEDULING (Insufficient CPU/Memory)

Impact:
  Affected Pods        : 9
  Affected Deployments : 1
  Namespaces           : 2
  Clusters             : prod-eu, prod-us

Change Correlation: NO
  No deployments or config changes detected in 1h window
```

### Timeline

```
18:14:23 UTC | WARN | prod-eu    | kube-system | FailedScheduling
             | Node cpu-pressure-node: Insufficient cpu

18:15:01 UTC | ERROR| prod-us    | payments    | BackOff
             | crashloop-pod: Back-off restarting failed container

18:16:47 UTC | ERROR| prod-eu    | payments    | Failed
             | bad-image-pod: ErrImagePull (manifest unknown)

18:18:12 UTC | WARN | prod-eu    | payments    | Unhealthy
             | Readiness probe failed (3 consecutive failures)
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (managed service or self-hosted)
- kubectl access to target clusters (for agent deployment)

### Step 1: Setup Database

Create the OpsAutopsy database and schema:

```bash
# Create database
createdb opsautopsy

# Create user (if needed)
psql -c "CREATE USER opsautopsy WITH PASSWORD 'opsautopsy';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE opsautopsy TO opsautopsy;"

# Apply schema
psql opsautopsy < db/schema.sql
```

For managed databases (RDS, Cloud SQL), create a dedicated user with appropriate permissions.

### Step 2: Install CLI

The OpsAutopsy CLI works on **Windows, macOS, and Linux**.

```bash
pip install opsautopsy
```

**Verify installation:**

```bash
opsautopsy --help
```

**Expected output:**

```
usage: opsautopsy [-h] {analyze,config} ...

OpsAutopsy – Kubernetes Post-Incident Forensics CLI

OpsAutopsy reconstructs incident timelines by correlating
Kubernetes events across clusters using historical data
stored in PostgreSQL.

options:
  -h, --help        show this help message and exit

Commands:
  {analyze,config}
    analyze         Analyze incidents from collected Kubernetes events
    config          Configure OpsAutopsy settings

Common examples:
  opsautopsy analyze --last-minutes 15
  opsautopsy analyze --namespace payments --last-minutes 60
  opsautopsy analyze --clusters prod-eu,prod-us --since 2026-01-15T16:00

Database configuration:
  opsautopsy config set-db postgresql://user:pass@localhost:5432/opsautopsy

Run 'opsautopsy <command> --help' for detailed options.
```

### Step 3: Configure Database Connection

Set the database URL for the CLI:

```bash
opsautopsy config set-db postgresql://opsautopsy:opsautopsy@localhost:5432/opsautopsy
```

**For remote databases:**

```bash
# AWS RDS
opsautopsy config set-db postgresql://user:pass@mydb.abc123.us-east-1.rds.amazonaws.com:5432/opsautopsy

# Google Cloud SQL
opsautopsy config set-db postgresql://user:pass@10.1.2.3:5432/opsautopsy

# Azure Database for PostgreSQL
opsautopsy config set-db postgresql://user@server:pass@server.postgres.database.azure.com:5432/opsautopsy
```

**Verify configuration:**

```bash
opsautopsy config show
```

### Step 4: Deploy Agent to Kubernetes

#### Create Namespace

```bash
kubectl create namespace opsautopsy
```

#### Create Database Secret

The agent reads the database connection from a Kubernetes Secret:

```bash
kubectl create secret generic opsautopsy-db \
  -n opsautopsy \
  --from-literal=url=postgresql://opsautopsy:opsautopsy@host:5432/opsautopsy
```

**For cloud databases, use the appropriate connection string:**

```bash
# Example with cloud database
kubectl create secret generic opsautopsy-db \
  -n opsautopsy \
  --from-literal=url=postgresql://user:pass@mydb.region.rds.amazonaws.com:5432/opsautopsy
```

#### Configure RBAC

The agent requires read-only access to core Kubernetes resources:

```bash
kubectl apply -f deploy/rbac.yaml
```

#### Deploy the Agent DaemonSet

```bash
kubectl apply -f deploy/agent-daemonset.yaml
```

**Verify deployment:**

```bash
kubectl get pods -n opsautopsy -l app=opsautopsy-agent
```

You should see one agent pod per node in your cluster.

#### Set Cluster ID

Each cluster must have a unique identifier. Edit `deploy/agent-daemonset.yaml`:

```yaml
env:
  - name: CLUSTER_ID
    value: prod-eu  # Change this for each cluster
```

**Important:** Use consistent, meaningful cluster IDs like `prod-eu`, `prod-us`, `staging-asia` to make multi-cluster analysis intuitive.

**Apply the updated configuration:**

```bash
kubectl apply -f deploy/agent-daemonset.yaml
```

### Step 5: Run Your First Analysis

```bash
# Analyze last 15 minutes
opsautopsy analyze --last-minutes 15

# Analyze last hour in specific namespace
opsautopsy analyze --namespace kube-system --last-minutes 60

# Multi-cluster analysis
opsautopsy analyze --clusters prod-eu,prod-us --last-minutes 30
```

---

## CLI Reference

### Analyze Command

```bash
opsautopsy analyze [OPTIONS]
```

**Time Options:**

```bash
--last-minutes MINUTES    Analyze last N minutes (e.g., --last-minutes 15)
--last-hours HOURS        Analyze last N hours (e.g., --last-hours 6)
--since TIMESTAMP         Start time (ISO 8601: 2026-01-15T16:00:00)
--until TIMESTAMP         End time (ISO 8601: 2026-01-15T18:00:00)
```

**Scope Options:**

```bash
--clusters CLUSTERS       Comma-separated cluster IDs (e.g., prod-eu,prod-us)
--namespace NAMESPACE     Filter by Kubernetes namespace
--deployment DEPLOYMENT   Filter by deployment name
--pod POD                 Filter by pod name pattern
```

**Output Options:**

```bash
--format FORMAT          Output format: text (default), json, yaml
--output FILE            Write output to file instead of stdout
--verbose                Show detailed event information
```

**Examples:**

```bash
# Last 15 minutes, all clusters
opsautopsy analyze --last-minutes 15

# Specific time window
opsautopsy analyze \
  --since 2026-01-15T16:00:00 \
  --until 2026-01-15T18:00:00

# Specific namespace, last hour
opsautopsy analyze --namespace payments --last-minutes 60

# Multi-cluster analysis
opsautopsy analyze --clusters prod-eu,prod-us --last-hours 2

# Export to JSON
opsautopsy analyze --last-minutes 30 --format json > incident.json

# Verbose output with all event details
opsautopsy analyze --last-minutes 15 --verbose
```

### Config Command

```bash
# Set database URL
opsautopsy config set-db <postgresql-url>

# Show current configuration
opsautopsy config show

# Clear configuration
opsautopsy config clear
```

**Examples:**

```bash
# Local database
opsautopsy config set-db postgresql://opsautopsy:opsautopsy@localhost:5432/opsautopsy

# Remote database with SSL
opsautopsy config set-db postgresql://user:pass@db.example.com:5432/opsautopsy?sslmode=require

# View current config
opsautopsy config show
```

---

## Agent Lifecycle & Operations

**The agent is designed for production safety:**

- **Stateless:** Can be restarted or upgraded without data loss
- **Continuous operation:** Runs 24/7, streaming events to database
- **Survives node restarts:** DaemonSet ensures automatic recovery
- **No impact on workloads:** Resource-limited and low-priority scheduling
- **Safe to redeploy:** Rolling updates with zero incident data loss

### Upgrading Agents

```bash
# Update image version in agent-daemonset.yaml
kubectl apply -f deploy/agent-daemonset.yaml

# Watch rollout
kubectl rollout status daemonset/opsautopsy-agent -n opsautopsy
```

### Monitoring Agent Health

```bash
# Check agent logs
kubectl logs -n opsautopsy -l app=opsautopsy-agent --tail=100

# Follow logs in real-time
kubectl logs -n opsautopsy -l app=opsautopsy-agent -f

# Check agent status
kubectl get pods -n opsautopsy -o wide

# Verify database connectivity
kubectl exec -n opsautopsy -it <agent-pod> -- env | grep OPSAUTOPSY
```

### Troubleshooting

**Agent pods not starting:**

```bash
# Check pod status
kubectl describe pod -n opsautopsy <pod-name>

# Verify secret exists
kubectl get secret -n opsautopsy opsautopsy-db

# Check RBAC permissions
kubectl auth can-i list events --as=system:serviceaccount:opsautopsy:opsautopsy-agent
```

**Database connection issues:**

```bash
# Test connection from agent pod
kubectl exec -n opsautopsy -it <agent-pod> -- \
  python -c "import psycopg2; print(psycopg2.connect('$OPSAUTOPSY_DB_URL'))"
```

**No events appearing in analysis:**

```bash
# Verify events are being collected
psql opsautopsy -c "SELECT COUNT(*), cluster_id FROM events GROUP BY cluster_id;"

# Check agent logs for errors
kubectl logs -n opsautopsy -l app=opsautopsy-agent | grep -i error
```

---

## Design Philosophy

### Separation of Concerns

**Collection ≠ Analysis**  
Agents collect, analyzer interprets. Clean boundaries enable independent scaling and safer operations.

### Read-Only by Design

Agents never mutate cluster state. Zero blast-radius risk during incidents.

### Cloud-Agnostic

Works with any Kubernetes distribution: EKS, GKE, AKS, on-prem, k3s, OpenShift, Rancher.

### Multi-Cluster First

Treats clusters as a dimension, not a boundary. Incidents don't respect cluster limits—why should your forensics tool?

### Post-Incident Intelligence

Complements real-time monitoring. Starts when alerts fire and understanding matters most.

---

## What OpsAutopsy Is NOT

| ❌ OpsAutopsy is NOT | ✅ Use Instead |
|---------------------|---------------|
| Real-time monitoring | Prometheus, Datadog |
| Alerting platform | PagerDuty, Opsgenie |
| Metrics scraping | Prometheus, VictoriaMetrics |
| Dashboard tool | Grafana, Kibana |
| Log aggregation | Loki, ELK Stack |

> **OpsAutopsy starts after alerts fire, when understanding matters most.**

---

## Current Status

### ✅ v1.0 Features

- [x] DaemonSet-based agents with read-only RBAC
- [x] Centralized PostgreSQL storage with time-series optimization
- [x] Multi-cluster event correlation
- [x] Incident classification engine (ImagePull, CrashLoop, OOM, Capacity)
- [x] Blast radius detection across clusters
- [x] CLI-based analysis and reporting
- [x] Cross-platform CLI support (Windows, macOS, Linux)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

**Quick Links:**
- 🐛 [Report a bug](https://github.com/yourorg/opsautopsy/issues/new?template=bug_report.md)
- 💡 [Request a feature](https://github.com/yourorg/opsautopsy/issues/new?template=feature_request.md)
- 💬 [Join discussions](https://github.com/yourorg/opsautopsy/discussions)

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details

---

**Built with ❤️ for SREs who deserve better incident post-mortems**