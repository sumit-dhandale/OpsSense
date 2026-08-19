# INC-2104

Title: gRPC Timeout to Inventory
Date: 2024-05-02
Service: Inventory
Severity: SEV2

Symptoms:
Add-to-cart gRPC calls to inventory timed out. Payments were unaffected.

Impact:
Cart updates failed; browse still worked from cache.

Logs:
```
DEADLINE_EXCEEDED: inventory.StockService/Reserve
```

Root Cause:
Network latency between the storefront and inventory AZ after a faulty CNI update, not application CPU.

Resolution:
Rolled back CNI, pinned inventory clients to local AZ.

Preventive Actions:
AZ-aware gRPC load balancing. Latency SLO per dependency.
