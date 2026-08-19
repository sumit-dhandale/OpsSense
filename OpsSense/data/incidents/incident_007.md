# INC-2501

Title: PostgreSQL Deadlock on Order Updates
Date: 2024-10-22
Service: Orders
Severity: SEV2

Symptoms:
Intermittent order status updates failed with deadlock. Payment capture succeeded but order stayed PENDING.

Impact:
Support tickets for missing order confirmation. No full outage.

Logs:
```
ERROR: deadlock detected
Process 4121 waits for ShareLock on transaction 8891
Statement: UPDATE orders SET status='PAID' WHERE id=...
```

Root Cause:
Two services updated the same order row in opposite column order (status vs captured_at), causing deadlocks under concurrency.

Resolution:
Canonical update order in a single orders service method. Retry with jitter on serialization failure.

Preventive Actions:
Lint for multi-statement updates. Chaos test concurrent capture + fulfill.
