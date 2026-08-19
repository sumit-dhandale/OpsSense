# INC-2390

Title: Kafka Rebalance Storm
Date: 2024-09-28
Service: Payments
Severity: SEV1

Symptoms:
Repeated Kafka rebalances. Consumers stopped processing. Related to lag but the trigger was session timeouts, not a slow message.

Impact:
Downstream settlement pipeline stalled. Risk of duplicate processing after rejoin.

Logs:
```
MemberId ... sending LeaveGroup
Rebalance failed: session.timeout.ms exceeded
max.poll.interval.ms exceeded while calling fraud feature enrichment
```

Root Cause:
Poll interval was 5 minutes but fraud enrichment on each record sometimes took longer during an Aerospike slowdown, causing the member to be kicked and a rebalance loop.

Resolution:
Raised max.poll.interval, processed fraud enrichment asynchronously, and paused the consumer on Aerospike errors.

Preventive Actions:
Do not do synchronous Aerospike calls inside poll loops. Rebalance rate alert.
