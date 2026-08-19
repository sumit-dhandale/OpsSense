# INC-1333

Title: Memory Pressure on Aerospike Nodes
Date: 2023-08-05
Service: Fraud Detection
Severity: SEV1

Symptoms:
Aerospike nodes swapped, then evicted indexes. Timeouts looked like INC-2841 from the client.

Impact:
Fraud lookups failed; payments fail-closed.

Logs:
```
AerospikeTimeoutException
kernel: Out of memory: Kill process asd
```

Root Cause:
Namespace memory-size undersized after a feature vector width increase (more bins per record). Memory pressure, not connection pools.

Resolution:
Raised memory-size, restored replicas, rolled back the wide feature.

Preventive Actions:
Capacity model tying feature vector bytes to Aerospike memory. Canary for schema width.
