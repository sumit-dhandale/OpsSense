# INC-1850

Title: Memory Pressure on API Gateway
Date: 2024-03-08
Service: Gateway
Severity: SEV2

Symptoms:
API gateway pods OOMKilled. Clients saw random 502s including payment authorize.

Impact:
Blip of errors across APIs, not a single datastore.

Logs:
```
Memory cgroup out of memory: Killed process envoy
upstream connect error or disconnect/reset before headers
```

Root Cause:
Access log payload included full authorization bodies. Memory pressure from logging, not Redis or Aerospike.

Resolution:
Truncated logs, raised memory limits temporarily, sampled debug logs.

Preventive Actions:
Log size budget. Memory working-set alerts on gateway.
