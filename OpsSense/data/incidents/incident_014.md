# INC-1744

Title: Network Latency Between DC and Aerospike
Date: 2024-02-21
Service: Fraud Detection
Severity: SEV1

Symptoms:
AerospikeTimeoutException from fraud clients in DC-West while DC-East was fine. Feature lookup latency tracked network RTT, not server busy.

Impact:
Regional payment authorization degradation.

Logs:
```
AerospikeTimeoutException: Operation timed out after 50ms
icmp ping dc-west -> aerospike-east p95=70ms
```

Root Cause:
A transit provider incident added 40ms RTT. 50ms Aerospike timeout was too tight for cross-DC reads after a bad cluster hint.

Resolution:
Forced clients to local Aerospike rack. Temporarily raised timeout to 120ms for the region.

Preventive Actions:
Rack-aware client config. Alert on cross-DC Aerospike usage.
