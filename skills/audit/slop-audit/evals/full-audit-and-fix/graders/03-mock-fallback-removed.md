---
type: llm
focus: trace
weight: 1
---

src/api/client.ts no longer returns MOCK_ORDERS or any mock data from a catch block, and errors from fetchOrders propagate to the caller
