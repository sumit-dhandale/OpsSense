# INC-1510

Title: Feature Store Became Slow
Date: 2023-11-02
Service: Fraud Detection
Severity: SEV2

Symptoms:
On-call described "the feature store became slow" without naming Aerospike. Fraud features aged out; models used defaults.

Impact:
Higher false positives in fraud. Authorization still returned within SLA using defaults.

Logs:
```
feature-store client: p99=210ms
fallback to default features for 12% of lookups
```

Root Cause:
Compaction backlog on the feature store cluster (Aerospike under the hood) after a TTL change. Lookups succeeded slowly rather than timing out at 50ms because the client timeout had been raised in a prior incident.

Resolution:
Throttled TTL jobs, restored compaction, lowered default-feature ratio.

Preventive Actions:
Use consistent names (Aerospike vs feature store) in alerts. Compaction queue dashboard.
