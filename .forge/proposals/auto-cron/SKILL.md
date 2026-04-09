---
name: auto-cron
description: "Auto-crystallized skill triggered by 6x cron calls (83% success across 2 sessions). Pattern: \"{\"action\":\"list\",\"includeDisabled\":true}...\""
metadata:
  openclaw:
    category: general
    aceforge:
      status: proposed
      proposed: 2026-03-31T04:36:50.065Z
      auto_generated: true
      candidate_occurrences: 6
      candidate_success_rate: 0.83
      first_seen: 2026-03-29T20:05:36.490Z
---

# auto-cron

## When to Use

Use this skill when you need to run: cron

## Detected Pattern

Arguments matching: {"action":"list","includeDisabled":true}...

## Instructions

1. Execute the `cron` tool with arguments matching the pattern above
2. Expected success rate: 83%
3. First observed: 2026-03-29T20:05:36.490Z

## Anti-Patterns

- Do NOT use if arguments don't match the detected pattern
- Do NOT use if context has changed significantly
- Do NOT use if error rate is elevated since 2026-03-29T20:05:36.490Z