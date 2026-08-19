# INC-1923

Title: Fraud Feature Lookup Latency Spike
Date: 2024-08-03
Service: Fraud Detection
Severity: SEV2

Symptoms:
Fraud feature lookup latency increased to 80ms. Downstream payment authorization stayed up but slowed.

Impact:
Authorization p95 rose from 120ms to 310ms. No hard outage; elevated error rate on retries.

Logs:
```
WARN fraud-client: feature lookup latency=82ms threshold=40ms
PaymentAuthorizationError: Fraud feature lookup latency increased to 80ms
```

Root Cause:
A hot feature key (device_fingerprint) caused Aerospike read amplification on a single partition.

Resolution:
Split the hot key, added client-side caching for stable device features, and raised the lookup timeout slightly.

Preventive Actions:
Hot-key dashboard on Aerospike partitions. Cache TTL for slowly changing fraud features.
