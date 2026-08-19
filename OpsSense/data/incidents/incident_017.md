# INC-1407

Title: Aerospike Hot Key Causing Latency
Date: 2023-09-17
Service: Fraud Detection
Severity: SEV1

Symptoms:
Single-bin hot key `merchant:global_limits` caused Aerospike timeout during peak traffic for all merchants.

Impact:
Payment authorization errors clustered on large merchants.

Logs:
```
AerospikeTimeoutException: Operation timed out after 50ms
hotkey: merchant:global_limits qps=18000
```

Root Cause:
A global limit document shared across all authorizations. Unlike INC-2841 (pool exhaustion), server CPU on one node was the bottleneck.

Resolution:
Sharded the key by merchant_id prefix and cached locally for 1s.

Preventive Actions:
Hot-key detection in Aerospike. Ban global singleton keys on the authorize path.
