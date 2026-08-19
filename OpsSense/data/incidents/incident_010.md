# INC-2215

Title: gRPC Timeout to Fraud Service
Date: 2024-07-11
Service: Fraud Detection
Severity: SEV1

Symptoms:
Payments reported gRPC timeout while fetching fraud features. Aerospike on the fraud side was healthy in isolation.

Impact:
Authorization fail-closed for high-risk countries. Error budget burned.

Logs:
```
DEADLINE_EXCEEDED: fraud.FeatureService/Lookup
PaymentAuthorizationError: Aerospike timeout while fetching fraud features  (client mislabel)
```

Root Cause:
A new Envoy retry policy multiplied load (retry storm) onto fraud pods. The client log line mentioned Aerospike because the stub error string was copied from an older SDK, which confused on-call.

Resolution:
Disabled retries on the Lookup RPC, scaled fraud pods, fixed the error string so Aerospike vs gRPC timeouts are distinct.

Preventive Actions:
Error taxonomy in the payments client. Retry budget on idempotent RPCs only.
