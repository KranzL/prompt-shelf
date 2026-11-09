---
type: llm
focus: trace
weight: 1
---

src/components/OrderForm.tsx no longer holds isLoading, hasError, and isSuccess as separate boolean useState slots; one status union, enum, or reducer replaces them
