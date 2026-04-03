"""
GO2SE Context Compression - 基于 Nano Claude Code Compaction 模块
===============================================================
两层压缩防止 session overflow:
- Layer 1: snip_old_tool_results - 截断旧工具结果
- Layer 2: compact_messages - LLM摘要旧消息
"""
from __future__ import annotations
from typing import Callable, Any

# ── Token 估算 ─────────────────────────────────────────────────────────────

def estimate_tokens(messages: list) -> int:
    """通过 content.length / 3.5 估算token数"""
    total_chars = 0
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    for v in block.values():
                        if isinstance(v, str):
                            total_chars += len(v)
        # tool_calls
        for tc in m.get("tool_calls", []):
            if isinstance(tc, dict):
                for v in tc.values():
                    if isinstance(v, str):
                        total_chars += len(v)
    return int(total_chars / 3.5)


def get_context_limit(model: str) -> int:
    """常见模型的context window限制"""
    CONTEXT_LIMITS = {
        "minimax/MiniMax-M2.7-highspeed": 100000,
        "minimax/MiniMax-M2.7": 100000,
        "minimax/MiniMax-M2.1": 100000,
        "claude-opus-4-6": 200000,
        "claude-sonnet-4-6": 200000,
        "claude-haiku-4-5-20251001": 200000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gemini-2.5-pro-preview-03-25": 1000000,
        "gemini-2.0-flash": 1000000,
        "gemini-1.5-pro": 2000000,
        "deepseek-chat": 64000,
        "deepseek-reasoner": 64000,
    }
    return CONTEXT_LIMITS.get(model, 128000)


# ── Layer 1: 截断旧工具结果 ────────────────────────────────────────────────

def snip_old_tool_results(
    messages: list,
    max_chars: int = 2000,
    preserve_last_n_turns: int = 6,
) -> list:
    """
    截断过长的旧工具消息，保留前一半+最后四分之一。
    从末尾保留 preserve_last_n_turns 条消息不变。
    """
    cutoff = max(0, len(messages) - preserve_last_n_turns)
    for i in range(cutoff):
        m = messages[i]
        if m.get("role") != "tool":
            continue
        content = m.get("content", "")
        if not isinstance(content, str) or len(content) <= max_chars:
            continue
        first_half = content[: max_chars // 2]
        last_quarter = content[-(max_chars // 4):]
        snipped = len(content) - len(first_half) - len(last_quarter)
        m["content"] = f"{first_half}\n[... {snipped} chars snipped ...]\n{last_quarter}"
    return messages


# ── Layer 2: 查找分割点 ────────────────────────────────────────────────────

def find_split_point(messages: list, keep_ratio: float = 0.3) -> int:
    """
    从后向前累加token，找到达到 keep_ratio 的分割点。
    返回 messages[:idx]=旧消息, messages[idx:]=新消息
    """
    total = estimate_tokens(messages)
    target = int(total * keep_ratio)
    running = 0
    for i in range(len(messages) - 1, -1, -1):
        running += estimate_tokens([messages[i]])
        if running >= target:
            return i
    return 0


# ── Layer 2: 消息压缩 ──────────────────────────────────────────────────────

def compact_messages(
    messages: list,
    llm_summarizer: Callable[[str], str],
) -> list:
    """
    使用LLM摘要旧消息，返回 [summary_msg, ack_msg, *recent_messages]

    Args:
        messages: 完整消息列表
        llm_summarizer: 接收文本返回摘要的函数
    Returns:
        压缩后的新消息列表
    """
    split = find_split_point(messages)
    if split <= 0:
        return messages

    old = messages[:split]
    recent = messages[split:]

    # 构建摘要请求文本
    old_text = ""
    for m in old:
        role = m.get("role", "?")
        content = m.get("content", "")
        if isinstance(content, str):
            old_text += f"[{role}]: {content[:500]}\n"
        elif isinstance(content, list):
            old_text += f"[{role}]: (structured content)\n"

    summary_prompt = (
        "Summarize the following conversation history concisely. "
        "Preserve key decisions, file paths, tool results, and context "
        "needed to continue:\n\n" + old_text
    )

    try:
        summary_text = llm_summarizer(summary_prompt)
    except Exception as e:
        # 摘要失败时降级: 直接丢弃旧消息
        summary_text = f"[Previous {split} messages omitted - summarization failed: {e}]"

    summary_msg = {
        "role": "user",
        "content": f"[Previous conversation summary]\n{summary_text}",
    }
    ack_msg = {
        "role": "assistant",
        "content": "明白了，我已了解之前对话的上下文。继续。",
    }
    return [summary_msg, ack_msg, *recent]


# ── 主入口: 智能压缩 ───────────────────────────────────────────────────────

def maybe_compact(
    state,
    config: dict,
    llm_summarizer: Callable[[str], str] = None,
) -> bool:
    """
    检查context是否接近满载，必要时执行两层压缩。

    Args:
        state: 有 .messages 列表的对象
        config: 包含 "model" 的配置字典
        llm_summarizer: 可选的LLM摘要函数，不提供时只做Layer1

    Returns:
        True if 执行了压缩
    """
    model = config.get("model", "")
    limit = get_context_limit(model)
    threshold = limit * 0.7  # 70% threshold

    if estimate_tokens(state.messages) <= threshold:
        return False

    # Layer 1: 截断旧工具结果
    snip_old_tool_results(state.messages)

    if estimate_tokens(state.messages) <= threshold:
        return True  # Layer 1 足够

    # Layer 2: 需要 LLM 摘要
    if llm_summarizer:
        state.messages = compact_messages(state.messages, llm_summarizer)
        return True

    return True  # 做了Layer1就算完成


# ── 便捷工具函数 ───────────────────────────────────────────────────────────

def get_session_token_stats(messages: list, model: str = "") -> dict:
    """返回当前会话的token统计信息"""
    total = estimate_tokens(messages)
    limit = get_context_limit(model) if model else 128000
    return {
        "estimated_tokens": total,
        "context_limit": limit,
        "usage_ratio": round(total / limit, 3) if limit > 0 else 0,
        "warning": "⚠️ 接近上限" if total > limit * 0.7 else "✅ 正常",
        "messages_count": len(messages),
    }


if __name__ == "__main__":
    # 简单测试
    test_messages = [
        {"role": "user", "content": "Hello world"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "tool", "content": "A" * 5000},
        {"role": "user", "content": "继续"},
    ]
    print(f"Token估算: {estimate_tokens(test_messages)}")
    print(f"Context限制(默认): {get_context_limit('')}")
    print(f"统计: {get_session_token_stats(test_messages)}")
