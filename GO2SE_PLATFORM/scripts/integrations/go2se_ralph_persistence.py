"""
GO2SE Ralph Persistence - 基于 OMX Ralph Contract 模块
============================================================
Ralph = 持久执行循环Owner
状态机: starting → executing → verifying → fixing → complete/failed/cancelled
持久化: JSON进度账本 + Markdown PRD文件

核心价值: 解决"任务执行到一半被中断"问题
"""
from __future__ import annotations

import json
import os
import uuid
import hashlib
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from typing import Optional, Any


# ── 常量 ─────────────────────────────────────────────────────────────────

RALPH_PHASES = ['starting', 'executing', 'verifying', 'fixing', 'complete', 'failed', 'cancelled']
RALPH_TERMINAL_PHASES = {'complete', 'failed', 'cancelled'}

RALPH_LEGACY_ALIASES = {
    'start': 'starting', 'started': 'starting',
    'execution': 'executing', 'execute': 'executing',
    'verify': 'verifying', 'verification': 'verifying',
    'fix': 'fixing',
    'complete': 'complete', 'completed': 'complete',
    'fail': 'failed', 'error': 'failed',
    'cancel': 'cancelled',
}

# ── 状态目录 ─────────────────────────────────────────────────────────────

STATE_DIR = Path.home() / ".go2se" / "ralph"
PRD_DIR = STATE_DIR / "plans"
PROGRESS_FILE = STATE_DIR / "ralph-progress.json"


# ── 数据模型 ─────────────────────────────────────────────────────────────

@dataclass
class RalphState:
    active: bool = False
    current_phase: str = 'starting'
    iteration: int = 0
    max_iterations: int = 50
    task_description: str = ""
    started_at: str = ""
    completed_at: str = ""
    error: str = ""
    notes: list = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RalphState":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProgressEntry:
    index: int
    text: str
    phase: str
    timestamp: str
    iteration: int


@dataclass
class VisualFeedback:
    score: float
    verdict: str  # pass | fail | warning
    category_match: bool
    differences: list
    suggestions: list
    reasoning: str = ""
    threshold: float = 90.0
    recorded_at: str = ""


# ── 工具函数 ─────────────────────────────────────────────────────────────

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _slugify(raw: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]+', '-', raw.lower().strip())
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:48] or 'ralph-task'


def _stable_json(obj: Any) -> str:
    import dataclasses
    if obj is None or (not isinstance(obj, (dict, list)) and not dataclasses.is_dataclass(obj)):
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))
    if isinstance(obj, list):
        return '[' + ','.join(_stable_json(i) for i in obj) + ']'
    if dataclasses.is_dataclass(obj):
        obj = dataclasses.asdict(obj)
    items = sorted(obj.items(), key=lambda x: x[0])
    entries = [f'{json.dumps(k)}:{_stable_json(v)}' for k, v in items]
    return '{' + ','.join(entries) + '}'


def _stable_json_pretty(obj: Any) -> str:
    return json.dumps(json.loads(_stable_json(obj)), indent=2)


def _ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PRD_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _is_valid_iso(value: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return datetime.fromisoformat(value) is not None


# ── 状态验证 ─────────────────────────────────────────────────────────────

def normalize_phase(raw_phase: str) -> tuple[Optional[str], Optional[str]]:
    """
    标准化phase名称。
    Returns: (normalized_phase, warning_or_error)
    """
    if not isinstance(raw_phase, str) or not raw_phase.strip():
        return None, "phase must be non-empty string"
    normalized = raw_phase.strip().lower()
    if normalized in RALPH_PHASES:
        return normalized, None
    if normalized in RALPH_LEGACY_ALIASES:
        return RALPH_LEGACY_ALIASES[normalized], f"normalized '{raw_phase}' -> {RALPH_LEGACY_ALIASES[normalized]}"
    return None, f"phase must be one of: {', '.join(RALPH_PHASES)}"


def validate_state(state: RalphState) -> tuple[bool, Optional[str]]:
    """
    验证RalphState合法性。
    Returns: (is_valid, error_message)
    """
    # phase验证
    if state.current_phase not in RALPH_PHASES:
        return False, f"invalid phase: {state.current_phase}"

    # terminal phase requires active=False
    if state.current_phase in RALPH_TERMINAL_PHASES and state.active:
        return False, f"terminal phase '{state.current_phase}' requires active=False"

    # iteration验证
    if not isinstance(state.iteration, int) or state.iteration < 0:
        return False, "iteration must be >= 0"

    # max_iterations验证
    if not isinstance(state.max_iterations, int) or state.max_iterations <= 0:
        return False, "max_iterations must be > 0"

    # timestamp验证
    if state.started_at and not _is_valid_iso(state.started_at):
        return False, "started_at must be ISO8601"
    if state.completed_at and not _is_valid_iso(state.completed_at):
        return False, "completed_at must be ISO8601"

    # active=True时自动设置默认值
    if state.active:
        if not state.started_at:
            state.started_at = _now_iso()
        if state.iteration == 0 and state.current_phase == 'starting':
            pass  # 初始状态正常

    return True, None


# ── 状态持久化核心 ───────────────────────────────────────────────────────

def load_state() -> RalphState:
    """从磁盘加载RalphState，不存在则返回初始状态"""
    if not STATE_DIR.exists():
        return RalphState()
    progress_file = STATE_DIR / "ralph-progress.json"
    if not progress_file.exists():
        return RalphState()
    try:
        data = json.loads(progress_file.read_text())
        return RalphState.from_dict(data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return RalphState()


def save_state(state: RalphState) -> None:
    """持久化RalphState到磁盘 (只写state字段，保留ledger)"""
    valid, err = validate_state(state)
    if not valid:
        raise ValueError(f"Invalid RalphState: {err}")
    _ensure_dirs()
    progress_file = STATE_DIR / "ralph-progress.json"
    # 合并: 读取现有ledger数据，只更新state字段
    existing = {}
    if progress_file.exists():
        try:
            existing = json.loads(progress_file.read_text())
        except Exception:
            existing = {}
    # 写入: state字段覆盖，ledger字段保留
    combined = {**existing, **state.to_dict()}
    progress_file.write_text(_stable_json_pretty(combined))


def transition(state: RalphState, new_phase: str) -> tuple[RalphState, str]:
    """
    状态转换。返回 (新状态, warning)。
    """
    normalized, err = normalize_phase(new_phase)
    if err and not normalized:
        raise ValueError(err)

    old_phase = state.current_phase
    state.current_phase = normalized
    state.notes.append(f"[{_now_iso()}] phase: {old_phase} → {normalized}")

    if normalized in RALPH_TERMINAL_PHASES:
        state.active = False
        state.completed_at = _now_iso()

    return state, ""


def advance_iteration(state: RalphState) -> RalphState:
    """推进迭代计数器"""
    if state.iteration >= state.max_iterations:
        state.current_phase = 'failed'
        state.active = False
        state.completed_at = _now_iso()
        state.error = f"max_iterations ({state.max_iterations}) exceeded"
        state.notes.append(f"[{_now_iso()}] FAILED: max iterations exceeded")
    else:
        state.iteration += 1
        state.notes.append(f"[{_now_iso()}] iteration {state.iteration}/{state.max_iterations}")
    return state


# ── PRD 文件管理 ────────────────────────────────────────────────────────

def load_prd(title: str = "") -> Optional[dict]:
    """加载PRD文件，不存在则返回None"""
    if not PRD_DIR.exists():
        return None
    slug = _slugify(title) if title else ""
    prd_file = PRD_DIR / f"prd-{slug}.md" if slug else None
    if prd_file and prd_file.exists():
        return {'path': str(prd_file), 'title': title}
    # 找最新的PRD
    prds = sorted(PRD_DIR.glob("prd-*.md"), key=lambda p: p.stat().st_mtime)
    if prds:
        latest = prds[-1]
        return {'path': str(latest), 'title': latest.stem[4:]}
    return None


def save_prd(title: str, content: str, task_description: str = "") -> str:
    """
    保存PRD为Markdown文件。
    Returns: 文件路径
    """
    _ensure_dirs()
    slug = _slugify(title)
    prd_file = PRD_DIR / f"prd-{slug}.md"
    counter = 1
    while prd_file.exists():
        prd_file = PRD_DIR / f"prd-{slug}-{counter}.md"
        counter += 1

    now = _now_iso()
    md_content = f"""# {title}

> Created by GO2SE Ralph Persistence | {now}

## Task Description
{task_description or '_No description_'}

## Progress Ledger
<!-- Auto-generated by Ralph -->

## Notes
<!-- Additional notes -->

## Metadata
- **Slug:** {slug}
- **Created:** {now}
- **SHA256:** {_sha256(content)}

---

{content}
"""
    prd_file.write_text(md_content, encoding='utf-8')
    return str(prd_file)


# ── Progress Ledger ──────────────────────────────────────────────────────

@dataclass
class ProgressLedger:
    schema_version: int = 2
    source: str = ""
    created_at: str = ""
    updated_at: str = ""
    entries: list = field(default_factory=list)
    visual_feedback: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def load_ledger() -> ProgressLedger:
    """加载进度账本"""
    ledger_file = STATE_DIR / "ralph-progress.json"
    if not ledger_file.exists():
        return ProgressLedger(created_at=_now_iso(), updated_at=_now_iso())
    try:
        data = json.loads(ledger_file.read_text())
        return ProgressLedger(
            schema_version=data.get('schema_version', 2),
            source=data.get('source', ''),
            created_at=data.get('created_at', _now_iso()),
            updated_at=data.get('updated_at', _now_iso()),
            entries=data.get('entries', []),
            visual_feedback=data.get('visual_feedback', []),
        )
    except (json.JSONDecodeError, TypeError):
        return ProgressLedger(created_at=_now_iso(), updated_at=_now_iso())


def save_ledger(ledger: ProgressLedger) -> None:
    """保存进度账本 (只写ledger字段，保留state)"""
    _ensure_dirs()
    ledger.updated_at = _now_iso()
    ledger_file = STATE_DIR / "ralph-progress.json"
    # 合并: 读取现有state数据，只更新ledger字段
    existing = {}
    if ledger_file.exists():
        try:
            existing = json.loads(ledger_file.read_text())
        except Exception:
            existing = {}
    # 写入: ledger字段覆盖，state字段保留
    combined = {**existing, **ledger.to_dict()}
    ledger_file.write_text(_stable_json_pretty(combined), encoding='utf-8')


def add_ledger_entry(ledger: ProgressLedger, text: str, phase: str, iteration: int) -> None:
    """添加进度条目"""
    entry = {
        'index': len(ledger.entries) + 1,
        'text': text,
        'phase': phase,
        'timestamp': _now_iso(),
        'iteration': iteration,
    }
    ledger.entries.append(entry)
    # 只保留最近100条
    ledger.entries = ledger.entries[-100:]


def add_visual_feedback(ledger: ProgressLedger, feedback: VisualFeedback) -> None:
    """添加视觉反馈"""
    fb_dict = {
        'recorded_at': feedback.recorded_at or _now_iso(),
        'score': feedback.score,
        'verdict': feedback.verdict,
        'category_match': feedback.category_match,
        'threshold': feedback.threshold,
        'passes_threshold': feedback.score >= feedback.threshold,
        'differences': feedback.differences,
        'suggestions': feedback.suggestions,
        'reasoning': feedback.reasoning,
        'next_actions': (feedback.suggestions + [f"Resolve: {d}" for d in feedback.differences])[:5],
    }
    ledger.visual_feedback.append(fb_dict)
    # 只保留最近30条
    ledger.visual_feedback = ledger.visual_feedback[-30:]


# ── Ralph 循环 ──────────────────────────────────────────────────────────

class RalphLoop:
    """
    Ralph持久执行循环。

    使用方式:
        ralph = RalphLoop("修复GO2SE内存泄漏")
        while ralph.can_continue():
            ralph.execute()
            ralph.verify()
            if ralph.needs_fix():
                ralph.fix()
        ralph.finish()
    """

    def __init__(self, task_description: str, max_iterations: int = 50):
        self.task_description = task_description
        self.max_iterations = max_iterations
        self.state = load_state()
        self.ledger = load_ledger()

        if not self.state.active:
            # 新建Ralph循环
            self.state = RalphState(
                active=True,
                current_phase='starting',
                iteration=0,
                max_iterations=max_iterations,
                task_description=task_description,
                started_at=_now_iso(),
            )
            self._save_all()

    def _save_all(self):
        save_state(self.state)
        save_ledger(self.ledger)

    def can_continue(self) -> bool:
        """检查是否可以继续执行"""
        return self.state.active and self.state.current_phase not in RALPH_TERMINAL_PHASES

    def needs_fix(self) -> bool:
        return self.state.current_phase == 'fixing'

    def execute(self):
        """执行阶段"""
        if self.state.current_phase == 'starting':
            self.state, _ = transition(self.state, 'executing')
        elif self.state.current_phase == 'fixing':
            self.state, _ = transition(self.state, 'executing')
        self._save_all()

    def verify(self, success: bool = True):
        """验证阶段"""
        if self.state.current_phase != 'executing':
            return
        phase = 'complete' if success else 'verifying'
        self.state, _ = transition(self.state, phase)
        if success:
            self.state = advance_iteration(self.state)
        self._save_all()

    def request_fix(self, reason: str = ""):
        """请求修复"""
        self.state, _ = transition(self.state, 'fixing')
        if reason:
            self.state.error = reason
        add_ledger_entry(self.ledger, f"Fix requested: {reason}", 'fixing', self.state.iteration)
        self._save_all()

    def finish(self, success: bool = True):
        """结束循环"""
        phase = 'complete' if success else 'failed'
        self.state, _ = transition(self.state, phase)
        if not success:
            self.state.error = self.state.error or "Task failed"
        add_ledger_entry(self.ledger, f"Finished: {phase}", phase, self.state.iteration)
        self._save_all()

    def add_note(self, text: str):
        """添加备注"""
        add_ledger_entry(self.ledger, text, self.state.current_phase, self.state.iteration)
        self._save_all()

    def get_status(self) -> dict:
        """获取当前状态摘要"""
        return {
            'active': self.state.active,
            'phase': self.state.current_phase,
            'iteration': self.state.iteration,
            'max_iterations': self.state.max_iterations,
            'task': self.state.task_description,
            'progress_pct': round(self.state.iteration / self.state.max_iterations * 100, 1) if self.state.max_iterations > 0 else 0,
            'ledger_entries': len(self.ledger.entries),
            'visual_feedback_count': len(self.ledger.visual_feedback),
            'started_at': self.state.started_at,
            'completed_at': self.state.completed_at,
            'error': self.state.error,
        }


# ── CLI 接口 ─────────────────────────────────────────────────────────────

def ralph_status() -> str:
    """CLI: 显示Ralph状态"""
    state = load_state()
    ledger = load_ledger()
    if not state.active and state.current_phase == 'starting' and state.iteration == 0:
        return "🪿 Ralph: 未激活 (无进行中的任务)"
    status = state.current_phase
    icon = {"starting": "🚀", "executing": "⚡", "verifying": "🔍", "fixing": "🔧", "complete": "✅", "failed": "❌", "cancelled": "🚫"}
    prog = round(state.iteration / state.max_iterations * 100, 1) if state.max_iterations > 0 else 0
    lines = [
        f"🪿 Ralph 状态: {icon.get(status, '❓')} {status}",
        f"   任务: {state.task_description[:60]}..." if len(state.task_description) > 60 else f"   任务: {state.task_description or '_无_'}",
        f"   进度: {state.iteration}/{state.max_iterations} ({prog}%)",
        f"   开始: {state.started_at[:19]}" if state.started_at else "",
        f"   错误: {state.error}" if state.error else "",
        f"   账本条目: {len(ledger.entries)}",
    ]
    return "\n".join([l for l in lines if l])


def ralph_start(task: str, max_iterations: int = 50) -> str:
    """CLI: 启动Ralph循环"""
    ralph = RalphLoop(task, max_iterations)
    return f"🚀 Ralph 已启动: {task[:50]}...\n状态: {ralph.state.current_phase}"


def ralph_complete() -> str:
    """CLI: 标记任务完成"""
    state = load_state()
    if state.current_phase in RALPH_TERMINAL_PHASES:
        return f"❌ Ralph 已处于 terminal phase: {state.current_phase}"
    ralph = RalphLoop(state.task_description)
    ralph.finish(success=True)
    return f"✅ Ralph 任务完成！迭代 {state.iteration} 次"


def ralph_fail(reason: str = "") -> str:
    """CLI: 标记任务失败"""
    state = load_state()
    ralph = RalphLoop(state.task_description)
    ralph.finish(success=False)
    return f"❌ Ralph 任务失败: {reason}"


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(ralph_status())
    elif cmd == "start":
        task = sys.argv[2] if len(sys.argv) > 2 else "GO2SE任务"
        max_it = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        print(ralph_start(task, max_it))
    elif cmd == "complete":
        print(ralph_complete())
    elif cmd == "fail":
        print(ralph_fail(sys.argv[2] if len(sys.argv) > 2 else ""))
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python go2se_ralph_persistence.py [status|start|complete|fail]")
