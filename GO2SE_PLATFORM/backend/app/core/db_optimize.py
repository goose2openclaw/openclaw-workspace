#!/usr/bin/env python3
"""
🪿 GO2SE 数据库优化 v11
- 索引优化
- 查询优化
- 数据迁移脚本
- 备份机制
"""

import os
import sqlite3
import logging
import json
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

logger = logging.getLogger("go2se")

# ─── 数据库路径 ───────────────────────────────────────────

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./go2se.db").replace("sqlite:///", "")
BACKUP_DIR = os.getenv("DB_BACKUP_DIR", "/root/.openclaw/workspace/GO2SE_PLATFORM/backups")
RETENTION_DAYS = int(os.getenv("DB_BACKUP_RETENTION", "7"))


# ─── 索引定义 ───────────────────────────────────────────

INDEX_DEFINITIONS = {
    # signals表索引
    "idx_signals_symbol_created": {
        "table": "signals",
        "columns": ["symbol", "created_at"],
        "unique": False,
    },
    "idx_signals_strategy_type": {
        "table": "signals",
        "columns": ["strategy_type", "created_at"],
        "unique": False,
    },
    "idx_signals_symbol_strategy": {
        "table": "signals",
        "columns": ["symbol", "strategy_type", "created_at"],
        "unique": False,
    },
    
    # trades表索引
    "idx_trades_symbol_created": {
        "table": "trades",
        "columns": ["symbol", "created_at"],
        "unique": False,
    },
    "idx_trades_order_id": {
        "table": "trades",
        "columns": ["order_id"],
        "unique": True,
    },
    "idx_trades_status": {
        "table": "trades",
        "columns": ["status", "created_at"],
        "unique": False,
    },
    
    # positions表索引
    "idx_positions_symbol": {
        "table": "positions",
        "columns": ["symbol"],
        "unique": False,
    },
    "idx_positions_strategy": {
        "table": "positions",
        "columns": ["strategy_type", "updated_at"],
        "unique": False,
    },
    
    # market_data表索引
    "idx_market_data_symbol_interval": {
        "table": "market_data",
        "columns": ["symbol", "interval", "timestamp"],
        "unique": False,
    },
    "idx_market_data_timestamp": {
        "table": "market_data",
        "columns": ["timestamp"],
        "unique": False,
    },
    
    # backtest_results表索引
    "idx_backtest_strategy_created": {
        "table": "backtest_results",
        "columns": ["strategy_type", "created_at"],
        "unique": False,
    },
    "idx_backtest_sharpe": {
        "table": "backtest_results",
        "columns": ["sharpe_ratio"],
        "unique": False,
    },
}


# ─── 连接管理 ───────────────────────────────────────────

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """FastAPI依赖注入"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── 索引管理 ───────────────────────────────────────────

def get_existing_indexes(conn: sqlite3.Connection) -> Dict[str, List[str]]:
    """获取现有索引"""
    cursor = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
    )
    return {row["name"]: row["sql"] for row in cursor.fetchall()}


def create_index_if_not_exists(conn: sqlite3.Connection, index_name: str, table: str, columns: List[str], unique: bool = False):
    """创建索引(如果不存在)"""
    existing = get_existing_indexes(conn)
    
    if index_name in existing:
        logger.info(f"  ✓ 索引已存在: {index_name}")
        return False
    
    columns_str = ", ".join(columns)
    unique_str = "UNIQUE" if unique else ""
    
    sql = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table} ({columns_str})"
    
    try:
        conn.execute(sql)
        conn.commit()
        logger.info(f"  ✓ 创建索引: {index_name}")
        return True
    except sqlite3.Error as e:
        logger.error(f"  ✗ 创建索引失败 {index_name}: {e}")
        return False


def optimize_database() -> Dict[str, Any]:
    """优化数据库 - 创建所有必要的索引"""
    logger.info("🔧 开始数据库优化...")
    
    results = {
        "indexes_created": 0,
        "indexes_skipped": 0,
        "analyze_performed": False,
        "vacuum_performed": False,
        "errors": [],
    }
    
    with get_db_connection() as conn:
        # 创建索引
        for index_name, config in INDEX_DEFINITIONS.items():
            try:
                created = create_index_if_not_exists(
                    conn,
                    index_name,
                    config["table"],
                    config["columns"],
                    config.get("unique", False)
                )
                if created:
                    results["indexes_created"] += 1
                else:
                    results["indexes_skipped"] += 1
            except Exception as e:
                results["errors"].append(f"{index_name}: {str(e)}")
        
        # 分析表(更新统计信息)
        try:
            conn.execute("ANALYZE")
            conn.commit()
            results["analyze_performed"] = True
            logger.info("  ✓ ANALYZE执行完成")
        except sqlite3.Error as e:
            logger.warning(f"  ⚠ ANALYZE失败: {e}")
    
    return results


def vacuum_database() -> bool:
    """清理数据库碎片"""
    try:
        with get_db_connection() as conn:
            conn.execute("VACUUM")
        logger.info("  ✓ VACUUM执行完成")
        return True
    except sqlite3.Error as e:
        logger.error(f"  ✗ VACUUM失败: {e}")
        return False


# ─── 查询优化 ───────────────────────────────────────────

class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.slow_queries: List[Dict] = []
        self.query_stats: Dict[str, Dict] = {}
    
    def log_query(self, query: str, duration_ms: float, rows: int = 0):
        """记录查询统计"""
        stats = self.query_stats.get(query, {
            "count": 0,
            "total_ms": 0,
            "min_ms": float("inf"),
            "max_ms": 0,
            "rows": 0,
        })
        
        stats["count"] += 1
        stats["total_ms"] += duration_ms
        stats["min_ms"] = min(stats["min_ms"], duration_ms)
        stats["max_ms"] = max(stats["max_ms"], duration_ms)
        stats["rows"] = max(stats["rows"], rows)
        
        self.query_stats[query] = stats
        
        # 慢查询告警
        if duration_ms > 1000:  # 超过1秒
            self.slow_queries.append({
                "query": query[:200],
                "duration_ms": duration_ms,
                "rows": rows,
                "timestamp": datetime.now().isoformat(),
            })
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
    
    def get_slow_queries(self, limit: int = 20) -> List[Dict]:
        """获取最慢的查询"""
        return sorted(self.slow_queries, key=lambda x: x["duration_ms"], reverse=True)[:limit]
    
    def get_stats(self) -> Dict:
        """获取查询统计"""
        return {
            "total_queries": len(self.query_stats),
            "slow_queries_count": len(self.slow_queries),
            "top_queries": sorted(
                [{"query": k, **v} for k, v in self.query_stats.items()],
                key=lambda x: x["total_ms"],
                reverse=True
            )[:10],
        }


query_optimizer = QueryOptimizer()


def execute_optimized_query(conn: sqlite3.Connection, query: str, params: tuple = (), explain: bool = False) -> List[Dict]:
    """执行优化查询"""
    start = time.time()
    
    try:
        if explain:
            cursor = conn.execute(f"EXPLAIN QUERY PLAN {query}", params)
        else:
            cursor = conn.execute(query, params)
        
        rows = cursor.fetchall()
        columns = cursor.description
        
        duration_ms = (time.time() - start) * 1000
        
        # 记录统计
        query_optimizer.log_query(query[:100], duration_ms, len(rows))
        
        if explain:
            return [dict(row) for row in rows]
        
        return [dict(zip([c[0] for c in columns], row)) for row in rows]
        
    except sqlite3.Error as e:
        logger.error(f"查询执行失败: {e}")
        raise


# ─── 数据迁移 ───────────────────────────────────────────

MIGRATIONS = [
    {
        "version": "v11_m001",
        "description": "添加backtest_results表",
        "sql": """
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_type VARCHAR(50) NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                initial_capital REAL NOT NULL,
                final_capital REAL NOT NULL,
                total_return REAL NOT NULL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                total_trades INTEGER,
                params TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
    {
        "version": "v11_m002",
        "description": "添加price_alerts表",
        "sql": """
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) NOT NULL,
                condition VARCHAR(20) NOT NULL,
                price REAL NOT NULL,
                active BOOLEAN DEFAULT 1,
                triggered BOOLEAN DEFAULT 0,
                callback_url VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                triggered_at DATETIME
            )
        """,
    },
    {
        "version": "v11_m003",
        "description": "添加strategy_configs表",
        "sql": """
            CREATE TABLE IF NOT EXISTS strategy_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                strategy_type VARCHAR(50) NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                weight REAL DEFAULT 0.0,
                max_position REAL DEFAULT 0.6,
                stop_loss REAL DEFAULT 0.10,
                take_profit REAL DEFAULT 0.30,
                interval_seconds INTEGER DEFAULT 60,
                params TEXT,
                version INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
    {
        "version": "v11_m004",
        "description": "添加db_migrations表",
        "sql": """
            CREATE TABLE IF NOT EXISTS db_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
]


def get_applied_migrations(conn: sqlite3.Connection) -> set:
    """获取已应用的迁移"""
    try:
        cursor = conn.execute("SELECT version FROM db_migrations")
        return {row["version"] for row in cursor.fetchall()}
    except sqlite3.OperationalError:
        return set()


def run_migrations() -> Dict[str, Any]:
    """运行所有待应用的迁移"""
    logger.info("🔄 开始数据迁移...")
    
    results = {
        "applied": [],
        "skipped": [],
        "errors": [],
    }
    
    with get_db_connection() as conn:
        applied = get_applied_migrations(conn)
        
        for migration in MIGRATIONS:
            version = migration["version"]
            
            if version in applied:
                results["skipped"].append(version)
                logger.info(f"  - {version}: 已应用, 跳过")
                continue
            
            try:
                # 执行迁移SQL
                for stmt in migration["sql"].split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        conn.execute(stmt)
                
                # 记录迁移
                conn.execute(
                    "INSERT OR IGNORE INTO db_migrations (version, description) VALUES (?, ?)",
                    (version, migration["description"])
                )
                conn.commit()
                
                results["applied"].append(version)
                logger.info(f"  ✓ {version}: {migration['description']}")
                
            except sqlite3.Error as e:
                results["errors"].append(f"{version}: {str(e)}")
                logger.error(f"  ✗ {version}: {e}")
    
    return results


# ─── 备份机制 ───────────────────────────────────────────

def ensure_backup_dir():
    """确保备份目录存在"""
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


def backup_database(reason: str = "manual") -> Optional[str]:
    """备份数据库"""
    ensure_backup_dir()
    
    if not os.path.exists(DB_PATH):
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"go2se_backup_{timestamp}_{reason}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        
        # 同时备份schema
        schema_path = backup_path + ".schema"
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type IN ('table', 'index') AND sql IS NOT NULL"
            )
            with open(schema_path, "w") as f:
                for row in cursor.fetchall():
                    f.write(row["sql"] + ";\n\n")
        
        # 压缩备份
        compressed_path = backup_path + ".gz"
        import gzip
        with open(backup_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(backup_path)
        os.remove(schema_path)
        
        logger.info(f"  ✓ 备份完成: {compressed_path}")
        return compressed_path
        
    except Exception as e:
        logger.error(f"  ✗ 备份失败: {e}")
        return None


def restore_database(backup_path: str) -> bool:
    """恢复数据库"""
    if not os.path.exists(backup_path):
        logger.error(f"备份文件不存在: {backup_path}")
        return False
    
    # 先创建当前数据库的备份
    backup_database(reason="pre_restore")
    
    try:
        import gzip
        with gzip.open(backup_path, "rb") as f_in:
            with open(DB_PATH, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"  ✓ 恢复完成: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ 恢复失败: {e}")
        return False


def cleanup_old_backups():
    """清理过期的备份文件"""
    ensure_backup_dir()
    
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed = 0
    
    for filename in os.listdir(BACKUP_DIR):
        filepath = os.path.join(BACKUP_DIR, filename)
        
        # 检查是否是备份文件
        if not filename.startswith("go2se_backup_"):
            continue
        
        # 检查修改时间
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime < cutoff:
            try:
                os.remove(filepath)
                removed += 1
            except OSError:
                pass
    
    if removed > 0:
        logger.info(f"  ✓ 清理了 {removed} 个过期备份")
    
    return removed


def get_backup_list() -> List[Dict]:
    """获取备份列表"""
    ensure_backup_dir()
    
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if not filename.startswith("go2se_backup_"):
            continue
        
        filepath = os.path.join(BACKUP_DIR, filename)
        stat = os.stat(filepath)
        
        # 解析备份信息
        parts = filename.replace("go2se_backup_", "").replace(".db.gz", "").split("_")
        
        backups.append({
            "filename": filename,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "reason": parts[-1] if len(parts) > 1 else "unknown",
        })
    
    return sorted(backups, key=lambda x: x["created_at"], reverse=True)


# ─── 数据库健康检查 ───────────────────────────────────────────

def check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    health = {
        "status": "healthy",
        "size_mb": 0,
        "tables": {},
        "indexes": {},
        "issues": [],
    }
    
    if not os.path.exists(DB_PATH):
        health["status"] = "unhealthy"
        health["issues"].append("数据库文件不存在")
        return health
    
    try:
        health["size_mb"] = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
        
        with get_db_connection() as conn:
            # 检查表
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row["name"] for row in cursor.fetchall()]
            
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                health["tables"][table] = cursor.fetchone()["count"]
            
            # 检查索引
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
            )
            health["indexes"] = [row["name"] for row in cursor.fetchall()]
            
            # 检查未使用索引的表
            for table in tables:
                cursor = conn.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # 简单检查: 表有数据但没有对应索引
                cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                row_count = cursor.fetchone()["count"]
                
                if row_count > 1000 and f"idx_{table}_symbol" not in str(health["indexes"]):
                    health["issues"].append(f"表 {table} 数据量大但可能缺少索引")
        
        # 警告条件
        if health["size_mb"] > 1000:
            health["issues"].append("数据库文件超过1GB，建议清理历史数据")
        
    except Exception as e:
        health["status"] = "unhealthy"
        health["issues"].append(str(e))
    
    return health
