from datetime import datetime, timedelta, timezone

from app.core.export_observability import ExportFailureStatsStore


def test_query_aggregates_failed_requests_and_ids():
    store = ExportFailureStatsStore(max_events=20)
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


def test_query_supports_doc_id_filter():
    store = ExportFailureStatsStore(max_events=20)
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


def test_query_respects_window_and_top_n():
    store = ExportFailureStatsStore(max_events=20)
    now = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)

    store.record_failure("doc_old", ["p1"], timestamp_utc=now - timedelta(minutes=90))
    store.record_failure("doc_c", ["p2"], timestamp_utc=now - timedelta(minutes=10))
    store.record_failure("doc_a", ["p3"], timestamp_utc=now - timedelta(minutes=9))
    store.record_failure("doc_b", ["p4"], timestamp_utc=now - timedelta(minutes=8))

    payload = store.query(window_minutes=60, now_utc=now, top_n=2)

    assert payload["summary"]["failed_requests"] == 3
    assert [item["doc_id"] for item in payload["by_doc"]] == ["doc_a", "doc_b"]
