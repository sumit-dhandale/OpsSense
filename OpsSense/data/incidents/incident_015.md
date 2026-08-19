# INC-1602

Title: Database Connection Timeout on User Service
Date: 2023-12-14
Service: Users
Severity: SEV2

Symptoms:
Login and profile reads hit Postgres connection timeouts. Checkout using cached sessions still worked.

Impact:
New logins failed. Existing sessions could still pay.

Logs:
```
psycopg2.OperationalError: connection timeout expired
remaining connection slots are reserved for SUPERUSER
```

Root Cause:
Connection pool leak in a new ORM session context manager. Same class of failure as payments Postgres pool exhaustion, different service.

Resolution:
Fixed session close on generator exit, bounced pods, added pool metrics.

Preventive Actions:
pytest fixture asserting connection count. Shared runbook: pool exhausted vs query slow.
