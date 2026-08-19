# INC-1188

Title: Network Latency to Redis Cluster
Date: 2023-06-20
Service: Payments
Severity: SEV2

Symptoms:
Idempotency Redis p99 rose with no command slowlog entries. Similar user-visible payment latency as Aerospike timeouts.

Impact:
Checkout retries. No data loss.

Logs:
```
redis: p99=45ms slowlog empty
tcp retransmits elevated on payments-to-redis path
```

Root Cause:
Noisy neighbor on a shared ToR switch, not Redis CPU or pool exhaustion.

Resolution:
Moved Redis NICs to a less contended pair, enabled jumbo frames consistently.

Preventive Actions:
Separate redis vs aerospike vs postgres latency panels so on-call does not assume one datastore.
