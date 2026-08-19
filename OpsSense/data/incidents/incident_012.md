# INC-1988

Title: CPU Saturation on Fraud Workers
Date: 2024-04-19
Service: Fraud Detection
Severity: SEV2

Symptoms:
Fraud feature lookup latency increased though Aerospike p99 was flat. Worker CPU sat at 98%.

Impact:
Authorization slowdown similar to INC-1923 from the payments side, different root cause.

Logs:
```
cpu.throttled_sec rising on fraud-worker
feature lookup latency=80ms
```

Root Cause:
A regex-heavy device rule compiled per request after a config push. CPU saturation, not datastore timeout.

Resolution:
Precompiled rules, rolled back the config, added CPU throttling alerts.

Preventive Actions:
Shadow-test rule packs. Distinguish app CPU vs Aerospike in the fraud dashboard.
