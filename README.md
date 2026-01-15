Got it 👍
Below is the **entire README.md wrapped inside a single code block**, so you can **copy–paste directly** into your repository without any formatting issues.

(No images, no special markup — clean Markdown only.)

---

```md
# OpsAutopsy

**OpsAutopsy** is a **cloud-agnostic, multi-cluster Kubernetes incident forensics engine**.

It focuses on **post-incident analysis**, not monitoring or alerting.  
OpsAutopsy reconstructs what happened during an incident by **correlating Kubernetes events, workload state, and change signals** into a single, time-ordered report — even across multiple clusters.

---

## Why OpsAutopsy?

Modern platforms have excellent observability tools, but during outages engineers still ask:

- What happened first?
- What changed?
- Why did the failure occur?
- How wide was the impact?
- Did this affect more than one cluster?

Most tools show **signals**.  
OpsAutopsy explains **incidents**.

---

## Core Idea

> **Post-incident intelligence, not real-time monitoring.**

OpsAutopsy:
- Does **not** replace Prometheus, Datadog, or cloud monitoring
- Works **after** an incident occurs
- Produces a **clear incident narrative**, not dashboards

---

## High-Level Architecture

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
Centralized PostgreSQL Database
(Events, Workload State, Metadata)
│
▼
OpsAutopsy Analyzer (CLI)
(Stateless, Multi-Cluster)

```

---

## Components

### 1. OpsAutopsy Agent (Per Cluster)

- **Deployment model:** DaemonSet  
- **Why DaemonSet:**  
  - One agent per node  
  - Captures node-level and scheduling-related signals  
  - Scales automatically with the cluster  

**Responsibilities**
- Watch Kubernetes **Events**
- Observe Pod and Deployment state
- Normalize timestamps (UTC)
- Attach `cluster_id`
- Persist data to centralized storage

**What it does NOT do**
- No analysis
- No alerting
- No mutation of cluster state

> The agent is intentionally **read-only and safe**.

---

### 2. Centralized Storage (PostgreSQL)

Kubernetes events are ephemeral and garbage-collected.  
OpsAutopsy uses **PostgreSQL** as durable incident memory.

**Why PostgreSQL**
- Strong time-based querying
- Easy correlation across clusters
- JSON support for flexible payloads
- Industry-standard and widely trusted

**Conceptual schema (simplified)**

```

## events

cluster_id
namespace
object_kind
object_name
reason
message
event_time (UTC)

## workload_state

cluster_id
namespace
workload_name
workload_type
status
restart_count
observed_time (UTC)

````

Long-term retention can later be archived to object storage.

---

### 3. OpsAutopsy Analyzer (CLI)

The analyzer is **stateless** and runs outside clusters.

**Responsibilities**
- Load data from PostgreSQL
- Filter by:
  - cluster(s)
  - namespace
  - time window
- Reconstruct incident timelines
- Detect:
  - Failure types (image pull, crash loop, OOM, capacity)
  - Blast radius
  - Change correlation
- Generate:
  - Incident summary
  - Human-readable timeline
  - Structured JSON output

**Example usage**
```bash
opsautopsy analyze \
  --clusters prod-eu,prod-us \
  --namespace payments \
  --since 6h
````

---

## Incident Model

OpsAutopsy treats incidents as **time-bounded correlated failures**, not single alerts.

### Incident Summary (Example)

```
Detected Issues:
- IMAGE_PULL_FAILURE
- CRASH_LOOP
- CAPACITY_SCHEDULING

Affected Pods    : 9
Affected Deploys : 1
Clusters Impacted: 2
Change Related   : NO
```

### Timeline (Evidence)

```
18:14 | FailedScheduling | cpu-pressure-pod
18:15 | BackOff          | crashloop-pod
18:16 | Failed           | bad-image-pod
```

* **Summary** = classification
* **Timeline** = proof

---

## Architectural Principles

* **Separation of concerns**
  Collection ≠ Analysis
* **Read-only by design**
  Zero blast-radius risk
* **Cloud-agnostic**
  No provider lock-in
* **Post-incident intelligence**
  Complements observability
* **Multi-cluster first**
  Cluster is a dimension, not a boundary

---

## What OpsAutopsy Is NOT

* Not a monitoring system
* Not an alerting platform
* Not a dashboard tool
* Not a replacement for Prometheus, Datadog, or cloud monitoring

> OpsAutopsy starts **after alerts fire**, when understanding matters most.

---

## Current Scope (v1)

### Included

* DaemonSet-based agents
* Centralized PostgreSQL storage
* Multi-cluster analysis
* Issue classification
* Blast radius detection
* CLI-based reports

### Explicitly Deferred

* Dashboards / UI
* Real-time alerting
* Metrics scraping
* Machine learning / anomaly detection

---

## One-Line Positioning

> **OpsAutopsy is a cloud-agnostic, multi-cluster Kubernetes incident forensics engine that reconstructs outages into clear, time-ordered explanations using centralized data.**

```

---
