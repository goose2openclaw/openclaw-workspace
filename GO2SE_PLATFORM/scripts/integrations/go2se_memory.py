"""
GO2SE Memory System - 基于 Nano Claude Code Memory 模块增强
===========================================================
4类记忆: user / feedback / project / reference
双层作用域: user (~/.go2se/memory) + project (.go2se/memory)

增强点:
- AI relevance ranking (可选)
- 记忆新鲜度警告
- index自动截断保护
"""
from __future__ import annotations

import re
import os
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── 路径配置 ────────────────────────────────────────────────────────────────

USER_MEMORY_DIR = Path.home() / ".go2se" / "memory"
PROJECT_MEMORY_DIR = Path(".go2se") / "memory"
INDEX_FILENAME = "MEMORY.md"
MAX_INDEX_LINES = 200
MAX_INDEX_BYTES = 25000

# ── 记忆类型 ────────────────────────────────────────────────────────────────

MEMORY_TYPES = ["user", "feedback", "project", "reference"]

MEMORY_TYPE_DESCRIPTIONS = {
    "user": "用户角色、目标、职责、知识 — 帮助个性化行为",
    "feedback": "用户给出的工作指导(纠正+确认) — 包含What/Why/How",
    "project": "进行中的工作、决策、非git历史记录的bug — 包含What/Why/How",
    "reference": "外部系统指针(issue trackers, dashboards, Slack等)",
}

WHAT_NOT_TO_SAVE = """
## ❌ 不保存到记忆
- 代码模式、架构、文件路径、项目结构 — 可从代码库推导
- Git历史、最近变更 — 用 git log / git blame
- 调试修复方案 — 修复已在代码中
- CLAUDE.md 中已有的内容
- 临时任务细节: 进行中的工作、临时状态、当前对话上下文
"""

MEMORY_FORMAT_TEMPLATE = """---
name: {name}
description: {description}
type: {type}
created: {created}
---

{content}
"""

# ── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class MemoryEntry:
    name: str
    description: str
    type: str
    content: str
    file_path: str = ""
    created: str = ""
    scope: str = "user"

    @classmethod
    def create(cls, name: str, description: str, memory_type: str, content: str, scope: str = "user") -> "MemoryEntry":
        return cls(
            name=name,
            description=description,
            type=memory_type,
            content=content,
            created=datetime.now().strftime("%Y-%m-%d"),
            scope=scope,
        )


# ── 工具函数 ────────────────────────────────────────────────────────────────

def _slugify(name: str) -> str:
    """转换为文件系统安全的slug (最大60字符)"""
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_\-]', '', name.lower().strip())
    return s[:60] or "memory"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 ---key: value---body 格式"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, parts[2].strip()


def _format_entry_md(entry: MemoryEntry) -> str:
    return MEMORY_FORMAT_TEMPLATE.format(
        name=entry.name,
        description=entry.description,
        type=entry.type,
        created=entry.created,
        content=entry.content,
    )


# ── 核心存储 ────────────────────────────────────────────────────────────────

def get_memory_dir(scope: str = "user") -> Path:
    if scope == "project":
        return PROJECT_MEMORY_DIR
    return USER_MEMORY_DIR


def save_memory(entry: MemoryEntry, scope: str = "user") -> str:
    """保存/更新记忆，自动重建index"""
    mem_dir = get_memory_dir(scope)
    mem_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(entry.name)
    fp = mem_dir / f"{slug}.md"
    fp.write_text(_format_entry_md(entry), encoding="utf-8")
    entry.file_path = str(fp)
    entry.scope = scope
    _rewrite_index(scope)
    return f"✅ 记忆已保存: [{entry.type}/{scope}] {entry.name}"


def delete_memory(name: str, scope: str = "user") -> str:
    """删除记忆并重建index"""
    mem_dir = get_memory_dir(scope)
    slug = _slugify(name)
    fp = mem_dir / f"{slug}.md"
    if fp.exists():
        fp.unlink()
    _rewrite_index(scope)
    return f"✅ 记忆已删除: {name} (scope: {scope})"


def load_entries(scope: str = "user") -> list[MemoryEntry]:
    """扫描所有.md文件并加载为MemoryEntry列表"""
    mem_dir = get_memory_dir(scope)
    if not mem_dir.exists():
        return []
    entries = []
    for fp in sorted(mem_dir.glob("*.md")):
        if fp.name == INDEX_FILENAME:
            continue
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        meta, body = parse_frontmatter(text)
        entries.append(MemoryEntry(
            name=meta.get("name", fp.stem),
            description=meta.get("description", ""),
            type=meta.get("type", "user"),
            content=body,
            file_path=str(fp),
            created=meta.get("created", ""),
            scope=scope,
        ))
    return sorted(entries, key=lambda e: e.name)


def load_index(scope: str = "all") -> list[MemoryEntry]:
    """从指定作用域加载记忆，'all'合并user+project"""
    if scope == "all":
        return load_entries("user") + load_entries("project")
    return load_entries(scope)


def search_memory(query: str, scope: str = "all") -> list[MemoryEntry]:
    """大小写不敏感关键词搜索"""
    q = query.lower()
    results = []
    for entry in load_index(scope):
        haystack = f"{entry.name} {entry.description} {entry.content}".lower()
        if q in haystack:
            results.append(entry)
    return results


def _rewrite_index(scope: str) -> None:
    """从.md文件重建MEMORY.md"""
    mem_dir = get_memory_dir(scope)
    if not mem_dir.exists():
        return
    index_path = mem_dir / INDEX_FILENAME
    entries = load_entries(scope)
    lines = [
        f"- [{e.name}]({Path(e.file_path).name}) — {e.description}"
        for e in entries
    ]
    index_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def get_index_content(scope: str = "user") -> str:
    """读取MEMORY.md内容，空则返回空字符串"""
    mem_dir = get_memory_dir(scope)
    index_path = mem_dir / INDEX_FILENAME
    if not index_path.exists():
        return ""
    return index_path.read_text(encoding="utf-8").strip()


# ── 记忆新鲜度 ─────────────────────────────────────────────────────────────

def memory_freshness_text(file_path: str) -> str:
    """根据文件修改时间返回新鲜度警告"""
    try:
        mtime = os.path.getmtime(file_path)
        age_days = (datetime.now().timestamp() - mtime) / 86400
        if age_days > 90:
            return f"⚠️ 已过期 ({int(age_days)}天前)"
        if age_days > 30:
            return f"⚡ 可能过期 ({int(age_days)}天前)"
        return ""
    except Exception:
        return ""


def truncate_index_content(raw: str) -> str:
    """截断MEMORY.md内容到行+字节限制，附加警告"""
    trimmed = raw.strip()
    content_lines = trimmed.split("\n")
    line_count = len(content_lines)
    byte_count = len(trimmed.encode())

    was_line_truncated = line_count > MAX_INDEX_LINES
    was_byte_truncated = byte_count > MAX_INDEX_BYTES

    if not was_line_truncated and not was_byte_truncated:
        return trimmed

    truncated = "\n".join(content_lines[:MAX_INDEX_LINES]) if was_line_truncated else trimmed
    if len(truncated.encode()) > MAX_INDEX_BYTES:
        raw_bytes = truncated.encode()
        cut = raw_bytes[:MAX_INDEX_BYTES].rfind(b"\n")
        truncated = raw_bytes[:cut if cut > 0 else MAX_INDEX_BYTES].decode(errors="replace")

    if was_byte_truncated and not was_line_truncated:
        reason = f"{byte_count:,} bytes (限制: {MAX_INDEX_BYTES:,})"
    elif was_line_truncated and not was_byte_truncated:
        reason = f"{line_count} lines (限制: {MAX_INDEX_LINES})"
    else:
        reason = f"{line_count} lines + {byte_count:,} bytes"

    warning = f"\n\n> ⚠️ MEMORY.md {reason}，只加载了部分。保持每条索引在150字符以内。"
    return truncated + warning


# ── AI Relevance 搜索 ───────────────────────────────────────────────────────

def find_relevant_memories(
    query: str,
    max_results: int = 5,
    use_ai: bool = False,
    config: Optional[dict] = None,
) -> list[dict]:
    """
    搜索相关记忆。
    策略1: 关键词搜索 (始终启用)
    策略2: AI relevance排序 (use_ai=True时启用)
    """
    keyword_results = search_memory(query)
    if not keyword_results:
        return []

    if not use_ai or not config:
        headers = load_entries("all")
        path_to_mtime = {e.file_path: os.path.getmtime(e.file_path) for e in headers if e.file_path}
        results = []
        for entry in keyword_results[:max_results]:
            mtime_s = path_to_mtime.get(entry.file_path, 0)
            results.append({
                "name": entry.name,
                "description": entry.description,
                "type": entry.type,
                "scope": entry.scope,
                "content": entry.content,
                "file_path": entry.file_path,
                "mtime_s": mtime_s,
                "freshness_text": memory_freshness_text(entry.file_path),
            })
        results.sort(key=lambda r: r["mtime_s"], reverse=True)
        return results[:max_results]

    # AI排序 (待集成LLM调用)
    return _ai_select_memories(query, keyword_results, max_results, config)


# ── 记忆上下文构建 ──────────────────────────────────────────────────────────

def get_memory_context(include_guidance: bool = False) -> str:
    """
    构建记忆上下文字符串用于系统提示词注入。
    合并user和project级别的MEMORY.md内容。
    """
    parts = []

    user_content = get_index_content("user")
    if user_content:
        parts.append(truncate_index_content(user_content))

    proj_content = get_index_content("project")
    if proj_content:
        parts.append(f"[项目级记忆]\n{truncate_index_content(proj_content)}")

    if not parts:
        return ""

    body = "\n\n".join(parts)
    if include_guidance:
        guidance = f"""## 记忆系统

4类记忆 (只保存无法从代码库推导的信息):
- **user** — 角色、目标、知识、偏好
- **feedback** — 工作指导(纠正+确认)，结构: 规则 + **Why:** + **How to apply:**
- **project** — 进行中的工作、决策、deadline，结构: 事实/决策 + **Why:** + **How to apply:**
- **reference** — 外部系统指针

保存时: 先保存到独立文件 → index自动更新
不保存: 代码模式、架构、git历史、已在CLAUDE.md中的内容、临时状态

{WHAT_NOT_TO_SAVE}

## MEMORY.md
"""
        return guidance + "\n\n" + body
    return body


# ── CLI 接口 ────────────────────────────────────────────────────────────────

def memory_save(name: str, memory_type: str, description: str, content: str, scope: str = "user") -> str:
    """CLI: 保存记忆"""
    if memory_type not in MEMORY_TYPES:
        return f"❌ type必须是: {MEMORY_TYPES}"
    entry = MemoryEntry.create(name, description, memory_type, content, scope)
    return save_memory(entry, scope)


def memory_delete(name: str, scope: str = "user") -> str:
    """CLI: 删除记忆"""
    return delete_memory(name, scope)


def memory_search(query: str, use_ai: bool = False, max_results: int = 5) -> str:
    """CLI: 搜索记忆"""
    results = find_relevant_memories(query, max_results=max_results, use_ai=use_ai)
    if not results:
        return f"没有找到与 '{query}' 相关的记忆"
    lines = [f"找到 {len(results)} 条相关记忆:\n"]
    for r in results:
        freshness = f"  {r['freshness_text']}" if r["freshness_text"] else ""
        lines.append(
            f"[{r['type']}/{r['scope']}] {r['name']}\n"
            f"  {r['description']}\n"
            f"  {r['content'][:200]}{'...' if len(r['content']) > 200 else ''}{freshness}"
        )
    return "\n\n".join(lines)


def memory_list(scope: str = "all") -> str:
    """CLI: 列出所有记忆"""
    entries = load_index(scope)
    if not entries:
        return "没有存储任何记忆"
    lines = [f"{len(entries)} 条记忆:\n"]
    for e in entries:
        freshness = memory_freshness_text(e.file_path)
        lines.append(f"[{e.type}/{e.scope}] {e.name} — {e.description}{f' {freshness}' if freshness else ''}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "save":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        mtype = sys.argv[3] if len(sys.argv) > 3 else "user"
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        content = sys.argv[5] if len(sys.argv) > 5 else ""
        print(memory_save(name, mtype, desc, content))
    elif cmd == "delete":
        print(memory_delete(sys.argv[2] if len(sys.argv) > 2 else ""))
    elif cmd == "search":
        print(memory_search(sys.argv[2] if len(sys.argv) > 2 else ""))
    else:
        print(memory_list())
