"""
导出失败可观测性存储（内存聚合）。
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any


class ExportFailureStatsStore:
    """导出失败统计存储。"""

    def __init__(self, max_events: int = 5000):
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._lock = Lock()

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

        with self._lock:
            self._events.append(
                {
                    "doc_id": doc_id,
                    "failed_ids": normalized_ids,
                    "timestamp": event_time,
                }
            )

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
        lower_bound = current_time - timedelta(minutes=window_minutes)

        with self._lock:
            events = list(self._events)

        filtered = [
            event
            for event in events
            if event["timestamp"] >= lower_bound and (doc_id is None or event["doc_id"] == doc_id)
        ]

        per_doc: dict[str, dict[str, Any]] = {}
        for event in filtered:
            doc_bucket = per_doc.setdefault(
                event["doc_id"],
                {
                    "doc_id": event["doc_id"],
                    "failed_requests": 0,
                    "failed_ids": 0,
                    "last_failed_at": event["timestamp"],
                },
            )
            doc_bucket["failed_requests"] += 1
            doc_bucket["failed_ids"] += len(event["failed_ids"])
            if event["timestamp"] > doc_bucket["last_failed_at"]:
                doc_bucket["last_failed_at"] = event["timestamp"]

        sorted_docs = sorted(
            per_doc.values(),
            key=lambda item: (-item["failed_requests"], -item["failed_ids"], item["doc_id"]),
        )[:top_n]

        by_doc = [
            {
                "doc_id": bucket["doc_id"],
                "failed_requests": bucket["failed_requests"],
                "failed_ids": bucket["failed_ids"],
                "last_failed_at": bucket["last_failed_at"].isoformat(),
            }
            for bucket in sorted_docs
        ]

        return {
            "window_minutes": window_minutes,
            "generated_at": current_time.isoformat(),
            "filters": {"doc_id": doc_id},
            "summary": {
                "failed_requests": len(filtered),
                "failed_ids": sum(len(event["failed_ids"]) for event in filtered),
            },
            "by_doc": by_doc,
        }

    def clear(self) -> None:
        """清空统计数据（测试场景）。"""
        with self._lock:
            self._events.clear()


_export_failure_stats_store = ExportFailureStatsStore()


def get_export_failure_stats_store() -> ExportFailureStatsStore:
    """获取导出失败统计存储单例。"""
    return _export_failure_stats_store


def clear_export_failure_stats() -> None:
    """清空导出失败统计（测试场景）。"""
    _export_failure_stats_store.clear()
