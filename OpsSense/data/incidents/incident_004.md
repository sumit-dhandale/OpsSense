# INC-3102

Title: Redis Latency on Session Cache
Date: 2025-02-01
Service: Sessions
Severity: SEV2

Symptoms:
Session reads from Redis slowed to 40–60ms. Users saw spinner delays after login, not payment failures.

Impact:
Increased bounce on authenticated pages. Payments were healthy.

Logs:
```
RedisTimeoutException: GET sess:* timed out after 20ms
slowlog: COMMAND GET, duration 54ms
```

Root Cause:
A large session blob (new A/B payload) exceeded typical Redis value size and evicted hotter keys, causing cache misses and extra Redis round trips.

Resolution:
Split session metadata from experiment payload. Enabled Redis lazy-free on eviction.

Preventive Actions:
Alert on Redis p99 and average value size. Cap session document bytes.
