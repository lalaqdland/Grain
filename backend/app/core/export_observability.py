"""
导出失败可观测性存储（SQLite 持久化）。
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from config import get_settings


class ExportFailureStatsStore:
    """导出失败统计存储。"""

    def __init__(self, db_path: str | None = None, max_events: int = 5000):
        # 兼容旧参数签名，SQLite实现不需要max_events限制。
        _ = max_events
        settings = get_settings()
        self._db_path = db_path or settings.export_stats_db_path
        self._lock = Lock()
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=10)

    def _init_db(self) -> None:
        parent_dir = os.path.dirname(self._db_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS export_failure_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        doc_id TEXT NOT NULL,
                        failed_ids_json TEXT NOT NULL,
                        failed_ids_count INTEGER NOT NULL,
                        event_ts_epoch REAL NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_export_failure_events_ts
                    ON export_failure_events(event_ts_epoch)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_export_failure_events_doc_ts
                    ON export_failure_events(doc_id, event_ts_epoch)
                    """
                )
                conn.commit()

    def record_failure(
        self,
        doc_id: str,
        failed_ids: list[str],
        timestamp_utc: datetime | None = None,
    ) -> None:
        """记录一次导出失败事件。"""
        normalized_ids = [failed_id for failed_id in failed_ids if failed_id]
        if not normalized_ids:
            return

        event_time = timestamp_utc or datetime.now(timezone.utc)
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        event_epoch = event_time.timestamp()

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO export_failure_events(
                        doc_id,
                        failed_ids_json,
                        failed_ids_count,
                        event_ts_epoch
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        json.dumps(normalized_ids, ensure_ascii=False),
                        len(normalized_ids),
                        event_epoch,
                    ),
                )
                conn.commit()

    def query(
        self,
        window_minutes: int,
        doc_id: str | None = None,
        top_n: int = 20,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        """按时间窗查询失败统计。"""
        current_time = now_utc or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        lower_bound_epoch = current_time.timestamp() - (window_minutes * 60)

        with self._lock:
            with self._connect() as conn:
                summary_row = conn.execute(
                    """
                    SELECT
                        COUNT(*) AS failed_requests,
                        COALESCE(SUM(failed_ids_count), 0) AS failed_ids
                    FROM export_failure_events
                    WHERE event_ts_epoch >= ?
                      AND (? IS NULL OR doc_id = ?)
                    """,
                    (lower_bound_epoch, doc_id, doc_id),
                ).fetchone()

                per_doc_rows = conn.execute(
                    """
                    SELECT
                        doc_id,
                        COUNT(*) AS failed_requests,
                        COALESCE(SUM(failed_ids_count), 0) AS failed_ids,
                        MAX(event_ts_epoch) AS last_failed_at
                    FROM export_failure_events
                    WHERE event_ts_epoch >= ?
                      AND (? IS NULL OR doc_id = ?)
                    GROUP BY doc_id
                    ORDER BY failed_requests DESC, failed_ids DESC, doc_id ASC
                    LIMIT ?
                    """,
                    (lower_bound_epoch, doc_id, doc_id, top_n),
                ).fetchall()

        by_doc = [
            {
                "doc_id": row[0],
                "failed_requests": int(row[1]),
                "failed_ids": int(row[2]),
                "last_failed_at": datetime.fromtimestamp(row[3], tz=timezone.utc).isoformat(),
            }
            for row in per_doc_rows
        ]

        return {
            "window_minutes": window_minutes,
            "generated_at": current_time.isoformat(),
            "filters": {"doc_id": doc_id},
            "summary": {
                "failed_requests": int(summary_row[0]) if summary_row else 0,
                "failed_ids": int(summary_row[1]) if summary_row else 0,
            },
            "by_doc": by_doc,
        }

    def get_storage_metrics(
        self,
        warn_bytes: int,
        critical_bytes: int,
    ) -> dict[str, Any]:
        """查询导出统计SQLite存储指标。"""
        safe_warn_bytes = max(1, int(warn_bytes))
        safe_critical_bytes = max(safe_warn_bytes, int(critical_bytes))

        db_size_bytes = os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0

        with self._lock:
            with self._connect() as conn:
                aggregate_row = conn.execute(
                    """
                    SELECT
                        COUNT(*) AS event_count,
                        MIN(event_ts_epoch) AS oldest_event_ts,
                        MAX(event_ts_epoch) AS newest_event_ts
                    FROM export_failure_events
                    """
                ).fetchone()

        event_count = int(aggregate_row[0]) if aggregate_row and aggregate_row[0] is not None else 0
        oldest_event_at = (
            datetime.fromtimestamp(aggregate_row[1], tz=timezone.utc).isoformat()
            if aggregate_row and aggregate_row[1] is not None
            else None
        )
        newest_event_at = (
            datetime.fromtimestamp(aggregate_row[2], tz=timezone.utc).isoformat()
            if aggregate_row and aggregate_row[2] is not None
            else None
        )

        if db_size_bytes >= safe_critical_bytes:
            level = "critical"
        elif db_size_bytes >= safe_warn_bytes:
            level = "warn"
        else:
            level = "ok"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "db_size_bytes": db_size_bytes,
            "event_count": event_count,
            "oldest_event_at": oldest_event_at,
            "newest_event_at": newest_event_at,
            "thresholds": {
                "warn_bytes": safe_warn_bytes,
                "critical_bytes": safe_critical_bytes,
            },
            "level": level,
        }

    def clear(self) -> None:
        """清空统计数据（测试场景）。"""
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM export_failure_events")
                conn.commit()

    def prune_old_events(self, retention_days: int = 30) -> dict[str, Any]:
        """
        清理超过 retention_days 天的旧事件，返回清理结果。
        """
        safe_retention = max(1, int(retention_days))
        cutoff_epoch = (datetime.now(timezone.utc).timestamp()) - (safe_retention * 86400)

        with self._lock:
            with self._connect() as conn:
                # 清理前统计
                before_count_row = conn.execute(
                    "SELECT COUNT(*) FROM export_failure_events"
                ).fetchone()
                before_count = int(before_count_row[0]) if before_count_row else 0

                # 执行清理
                deleted = conn.execute(
                    "DELETE FROM export_failure_events WHERE event_ts_epoch < ?",
                    (cutoff_epoch,),
                ).rowcount
                conn.commit()

                # 清理后统计
                after_count_row = conn.execute(
                    "SELECT COUNT(*) FROM export_failure_events"
                ).fetchone()
                after_count = int(after_count_row[0]) if after_count_row else 0

        return {
            "retention_days": safe_retention,
            "cutoff_epoch": cutoff_epoch,
            "before_count": before_count,
            "deleted_count": deleted,
            "remaining_count": after_count,
        }

    def get_monitoring_status(
        self,
        marian_runtime_info: dict[str, Any],
        marian_failure_rate_warn: float,
        marian_failure_rate_critical: float,
        export_failure_requests_warn: int,
        export_failure_requests_critical: int,
        window_minutes: int = 60,
    ) -> dict[str, Any]:
        """
        聚合所有健康指标，返回统一监控状态。
        """
        # Marian 健康指标
        marian_failure_rate = float(marian_runtime_info.get("generation_failure_rate", 0.0))
        if marian_failure_rate >= marian_failure_rate_critical:
            marian_level = "critical"
        elif marian_failure_rate >= marian_failure_rate_warn:
            marian_level = "warn"
        else:
            marian_level = "ok"

        marian_indicators = {
            "level": marian_level,
            "generation_failure_rate": marian_failure_rate,
            "generation_attempts": marian_runtime_info.get("generation_attempts", 0),
            "generation_failures": marian_runtime_info.get("generation_failures", 0),
            "model_loaded": marian_runtime_info.get("model_loaded", False),
            "status": marian_runtime_info.get("status", "unknown"),
            "thresholds": {
                "warn": marian_failure_rate_warn,
                "critical": marian_failure_rate_critical,
            },
        }

        # 导出失败指标（最近时间窗口）
        export_query = self.query(window_minutes=window_minutes)
        failed_requests = export_query["summary"]["failed_requests"]

        if failed_requests >= export_failure_requests_critical:
            export_level = "critical"
        elif failed_requests >= export_failure_requests_warn:
            export_level = "warn"
        else:
            export_level = "ok"

        export_indicators = {
            "level": export_level,
            "failed_requests": failed_requests,
            "failed_ids": export_query["summary"]["failed_ids"],
            "window_minutes": window_minutes,
            "thresholds": {
                "warn": export_failure_requests_warn,
                "critical": export_failure_requests_critical,
            },
        }

        # 存储健康指标
        storage_metrics = self.get_storage_metrics(
            warn_bytes=10 * 1024 * 1024,
            critical_bytes=50 * 1024 * 1024,
        )
        storage_indicators = {
            "level": storage_metrics["level"],
            "db_size_bytes": storage_metrics["db_size_bytes"],
            "event_count": storage_metrics["event_count"],
        }

        # 整体级别：取最严重
        all_levels = [marian_level, export_level, storage_metrics["level"]]
        if "critical" in all_levels:
            overall_level = "critical"
        elif "warn" in all_levels:
            overall_level = "warn"
        else:
            overall_level = "ok"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_level": overall_level,
            "marian": marian_indicators,
            "export_failures": export_indicators,
            "storage": storage_indicators,
        }


_export_failure_stats_store: ExportFailureStatsStore | None = None


def get_export_failure_stats_store() -> ExportFailureStatsStore:
    """获取导出失败统计存储单例。"""
    global _export_failure_stats_store
    target_path = get_settings().export_stats_db_path
    if _export_failure_stats_store is None or _export_failure_stats_store.db_path != target_path:
        _export_failure_stats_store = ExportFailureStatsStore(db_path=target_path)
    return _export_failure_stats_store


def clear_export_failure_stats() -> None:
    """清空导出失败统计（测试场景）。"""
    get_export_failure_stats_store().clear()
