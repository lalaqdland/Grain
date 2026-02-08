from datetime import datetime, timedelta, timezone

from app.core.export_observability import ExportFailureStatsStore


def test_query_aggregates_failed_requests_and_ids(tmp_path):
    store = ExportFailureStatsStore(db_path=str(tmp_path / "stats.db"), max_events=20)
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    store.record_failure("doc_a", ["p1", "p2"], timestamp_utc=now - timedelta(minutes=30))
    store.record_failure("doc_a", ["p3"], timestamp_utc=now - timedelta(minutes=10))
    store.record_failure("doc_b", ["p9"], timestamp_utc=now - timedelta(minutes=5))

    payload = store.query(window_minutes=60, now_utc=now, top_n=10)

    assert payload["summary"]["failed_requests"] == 3
    assert payload["summary"]["failed_ids"] == 4
    assert payload["by_doc"][0]["doc_id"] == "doc_a"
    assert payload["by_doc"][0]["failed_requests"] == 2
    assert payload["by_doc"][0]["failed_ids"] == 3


def test_query_supports_doc_id_filter(tmp_path):
    store = ExportFailureStatsStore(db_path=str(tmp_path / "stats.db"), max_events=20)
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    store.record_failure("doc_a", ["p1"], timestamp_utc=now - timedelta(minutes=15))
    store.record_failure("doc_b", ["p2", "p3"], timestamp_utc=now - timedelta(minutes=12))

    payload = store.query(window_minutes=60, doc_id="doc_b", now_utc=now)

    assert payload["filters"]["doc_id"] == "doc_b"
    assert payload["summary"]["failed_requests"] == 1
    assert payload["summary"]["failed_ids"] == 2
    assert payload["by_doc"] == [
        {
            "doc_id": "doc_b",
            "failed_requests": 1,
            "failed_ids": 2,
            "last_failed_at": (now - timedelta(minutes=12)).isoformat(),
        }
    ]


def test_query_respects_window_and_top_n(tmp_path):
    store = ExportFailureStatsStore(db_path=str(tmp_path / "stats.db"), max_events=20)
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    store.record_failure("doc_old", ["p1"], timestamp_utc=now - timedelta(minutes=90))
    store.record_failure("doc_c", ["p2"], timestamp_utc=now - timedelta(minutes=10))
    store.record_failure("doc_a", ["p3"], timestamp_utc=now - timedelta(minutes=9))
    store.record_failure("doc_b", ["p4"], timestamp_utc=now - timedelta(minutes=8))

    payload = store.query(window_minutes=60, now_utc=now, top_n=2)

    assert payload["summary"]["failed_requests"] == 3
    assert [item["doc_id"] for item in payload["by_doc"]] == ["doc_a", "doc_b"]


def test_query_persists_across_store_instances(tmp_path):
    db_path = str(tmp_path / "stats.db")
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    first_store = ExportFailureStatsStore(db_path=db_path)
    first_store.record_failure("doc_a", ["p1", "p2"], timestamp_utc=now - timedelta(minutes=5))

    second_store = ExportFailureStatsStore(db_path=db_path)
    payload = second_store.query(window_minutes=60, now_utc=now)

    assert payload["summary"]["failed_requests"] == 1
    assert payload["summary"]["failed_ids"] == 2
    assert payload["by_doc"][0]["doc_id"] == "doc_a"


def test_storage_metrics_include_size_and_event_bounds(tmp_path):
    store = ExportFailureStatsStore(db_path=str(tmp_path / "stats.db"))
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    store.record_failure("doc_a", ["p1"], timestamp_utc=now - timedelta(minutes=6))
    store.record_failure("doc_a", ["p2", "p3"], timestamp_utc=now - timedelta(minutes=1))

    metrics = store.get_storage_metrics(
        warn_bytes=10**9,
        critical_bytes=10**10,
    )

    assert metrics["db_size_bytes"] > 0
    assert metrics["event_count"] == 2
    assert metrics["oldest_event_at"] == (now - timedelta(minutes=6)).isoformat()
    assert metrics["newest_event_at"] == (now - timedelta(minutes=1)).isoformat()
    assert metrics["level"] == "ok"
    assert metrics["thresholds"]["warn_bytes"] == 10**9
    assert metrics["thresholds"]["critical_bytes"] == 10**10


def test_storage_metrics_level_warn_and_critical(tmp_path):
    store = ExportFailureStatsStore(db_path=str(tmp_path / "stats.db"))
    store.record_failure("doc_a", ["p1"])

    base_metrics = store.get_storage_metrics(
        warn_bytes=10**9,
        critical_bytes=10**10,
    )
    db_size = base_metrics["db_size_bytes"]
    assert db_size > 0

    warn_metrics = store.get_storage_metrics(
        warn_bytes=max(1, db_size - 1),
        critical_bytes=db_size + 1024,
    )
    assert warn_metrics["level"] == "warn"

    critical_metrics = store.get_storage_metrics(
        warn_bytes=max(1, db_size - 1),
        critical_bytes=db_size,
    )
    assert critical_metrics["level"] == "critical"
