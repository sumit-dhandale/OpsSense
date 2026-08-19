# INC-2650

Title: PostgreSQL Connection Pool Exhaustion
Date: 2024-12-09
Service: Payments
Severity: SEV1

Symptoms:
Payment writes to Postgres hung. HikariCP logs showed threads waiting for connections. Authorization API returned 503.

Impact:
Complete payment write outage for 16 minutes.

Logs:
```
HikariPool: Connection is not available, request timed out after 30000ms
FATAL: remaining connection slots are reserved
```

Root Cause:
A reporting query held transactions open, exhausting the Postgres connection pool. Application pool (30) plus BI tools exceeded max_connections.

Resolution:
Killed the long query, moved reporting to a replica, reduced Hikari maximumPoolSize, and added statement_timeout.

Preventive Actions:
PgBouncer. Alert on waiting clients and idle-in-transaction age.
