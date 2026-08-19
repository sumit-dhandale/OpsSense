# INC-2841

Title: Aerospike Timeout During Peak Traffic
Date: 2024-11-12
Service: Fraud Detection
Severity: SEV1

Symptoms:
Fraud feature lookups started timing out during the evening peak. Payment authorization p95 climbed as the fraud client waited on Aerospike.

Impact:
Payment authorization latency increased significantly. Checkout conversion dropped for about 28 minutes.

Logs:
```
AerospikeTimeoutException:
Operation timed out after 50ms
PaymentAuthorizationError: fraud feature lookup failed
```

Root Cause:
Connection pool exhaustion caused requests to wait for available connections. Peak traffic exceeded the configured Aerospike client pool.

Resolution:
Increased connection pool size and introduced backpressure so authorization could fail fast instead of queueing.

Preventive Actions:
Added connection pool monitoring and alerts. Load-tested fraud feature lookup at 2x peak QPS.
