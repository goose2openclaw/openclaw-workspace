---
name: auto-subagents
description: "Auto-crystallized skill triggered by 9x subagents calls (100% success across 2 sessions). Pattern: \"{\"action\":\"list\"}...\""
metadata:
  openclaw:
    category: general
    aceforge:
      status: proposed
      proposed: 2026-03-31T04:36:44.778Z
      auto_generated: true
      candidate_occurrences: 9
      candidate_success_rate: 1
      first_seen: 2026-03-29T15:12:31.049Z
---

# auto-subagents

## When to Use

Use this skill when you need to run: subagents

## Detected Pattern

Arguments matching: {"action":"list"}...

## Instructions

1. Execute the `subagents` tool with arguments matching the pattern above
2. Expected success rate: 100%
3. First observed: 2026-03-29T15:12:31.049Z

## Anti-Patterns

- Do NOT use if arguments don't match the detected pattern
- Do NOT use if context has changed significantly
- Do NOT use if error rate is elevated since 2026-03-29T15:12:31.049Z