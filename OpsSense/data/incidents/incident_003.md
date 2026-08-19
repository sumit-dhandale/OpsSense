# INC-1721

Title: Payment Authorization Latency Increase
Date: 2024-06-18
Service: Payments
Severity: SEV1

Symptoms:
Payment authorization latency increased across all card brands. Fraud evaluation was in the critical path.

Impact:
Checkout timeouts. Revenue impact estimated at $180k during the window.

Logs:
```
PaymentAuthorizationError: upstream fraud.eval exceeded 200ms budget
grpc deadline exceeded calling fraud.FeatureService/Lookup
```

Root Cause:
Fraud service gRPC deadline was tighter than the Aerospike client timeout, so payments saw generic deadline errors rather than Aerospike timeouts.

Resolution:
Aligned timeouts (Aerospike 40ms, fraud RPC 80ms, payments budget 150ms) and added a fail-open path for low-risk transactions.

Preventive Actions:
Timeout budget diagram in runbooks. Synthetic check on fraud.eval p99.
