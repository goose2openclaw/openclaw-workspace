---
name: exec-polling-best-practices
description: "Prevent exec retry storms and poll timeout cascades. Detects rapid 3+ exec calls and long-running poll loops, applying batching and timeout guards automatically."
metadata:
  openclaw:
    category: reliability
    aceforge:
      status: proposed
      proposed: 2026-03-30T05:10:59.129Z
---

# exec-polling-best-practices

## exec-polling-best-practices Skill

### Trigger Conditions
- exec called 3+ times within same assistant turn (retry storm)
- exec with poll/timeout > 5 minutes
- process.poll(timeout > 300000)

### Behavior
1. **Batch commands**: If 3+ exec calls within same turn, batch into single exec with `&&` or `;`
2. **Guard against silent failures**: Add `set -e` or `|| true` guards
3. **Poll timeout cap**: If poll > 5min needed, use `yieldMs=300000` + background, then poll with 60s intervals
4. **External API rate limits**: Before calling external APIs (EvoMap, etc.) in loops, check rate limit docs and add `sleep` delays
5. **Checkpoint design**: For long tasks (>10min), design as background exec + periodic status checks, not single blocking poll

### Anti-Patterns to Avoid
- `poll(timeout=1200000)` — never single 20min poll
- Rapid exec retry without examining failure output first
- Not capturing `retry_after_ms` from API responses

