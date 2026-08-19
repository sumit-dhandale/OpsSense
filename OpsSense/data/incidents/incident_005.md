# INC-3011

Title: Redis Connection Timeout During Checkout
Date: 2025-01-14
Service: Payments
Severity: SEV1

Symptoms:
Checkout Redis (idempotency keys) timed out. Clients retried and created duplicate authorization attempts.

Impact:
Duplicate charges risk; authorization error rate 9%.

Logs:
```
JedisConnectionException: Could not get a resource from the pool
PaymentAuthorizationError: idempotency redis timeout
```

Root Cause:
Redis connection pool exhaustion on the payments service. MaxTotal was 16 under 400 checkout threads. Same failure shape as Aerospike pool issues, different datastore.

Resolution:
Increased pool size, set blockWhenExhausted with a short wait, and added circuit breaking around Redis.

Preventive Actions:
Pool utilization metrics for Redis and Aerospike clients. Shared playbook for connection pool saturation.
