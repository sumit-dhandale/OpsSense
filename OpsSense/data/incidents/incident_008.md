# INC-2408

Title: Kafka Consumer Lag on Payment Events
Date: 2024-09-30
Service: Payments
Severity: SEV2

Symptoms:
payment.authorized consumer lag grew to 12 minutes. Fraud scoring of settled payments was delayed, not live authorization.

Impact:
Delayed risk review. Live checkout still used synchronous fraud lookup.

Logs:
```
kafka: consumer lag partition=7 lag=450000
CommitFailedException: Offset commit cannot be completed
```

Root Cause:
A poison payload with an oversized metadata field made processing time jump; the consumer thread blocked on JSON parse.

Resolution:
Skipped the bad offset, added payload size limits, and scaled consumers.

Preventive Actions:
Lag alerts at 30s. Schema max size on payment events.
