---
name: auto-cron
description: "Auto-crystallized skill triggered by 6x cron calls (100% success across 2 sessions). Pattern: \"{\"action\":\"list\",\"includeDisabled\":true}...\""
metadata:
  openclaw:
    category: general
    aceforge:
      status: proposed
      proposed: 2026-03-29T11:22:13.733Z
      auto_generated: true
      candidate_occurrences: 6
      candidate_success_rate: 1
      first_seen: 2026-03-28T15:20:24.409Z
---

# auto-cron

## When to Use

Use this skill when you need to run: cron

## Detected Pattern

Arguments matching: {"action":"list","includeDisabled":true}...

## Instructions

1. Execute the `cron` tool with arguments matching the pattern above
2. Expected success rate: 100%
3. First observed: 2026-03-28T15:20:24.409Z

## Anti-Patterns

- Do NOT use if arguments don't match the detected pattern
- Do NOT use if context has changed significantly
- Do NOT use if error rate is elevated since 2026-03-28T15:20:24.409Z