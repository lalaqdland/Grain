from io import BytesIO

from docx import Document

from app.core.xml_processor import get_processor
import app.api.v1.rewrite as rewrite_api


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def upload_sample_doc(client, sample_docx_bytes):
    response = client.post(
        "/api/v1/upload",
        files={"file": ("sample.docx", sample_docx_bytes, DOCX_MIME)},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_upload_ids_are_registered(client, sample_docx_bytes):
    uploaded = upload_sample_doc(client, sample_docx_bytes)
    processor = get_processor(uploaded["id"])

    paragraph_ids = [paragraph["id"] for paragraph in uploaded["paragraphs"]]
    assert paragraph_ids, "上传后至少应有一个非空段落"
    for paragraph_id in paragraph_ids:
        assert paragraph_id in processor.paragraph_map


def test_get_uploaded_document_success(client, sample_docx_bytes):
    uploaded = upload_sample_doc(client, sample_docx_bytes)

    response = client.get(f"/api/v1/upload/documents/{uploaded['id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["id"] == uploaded["id"]
    assert payload["data"]["total_paragraphs"] == uploaded["total_paragraphs"]


def test_get_uploaded_document_not_found(client):
    response = client.get("/api/v1/upload/documents/doc_missing")

    assert response.status_code == 404
    assert "文档不存在" in response.json()["detail"]


def test_export_rejects_invalid_paragraph_id(client, sample_docx_bytes):
    uploaded = upload_sample_doc(client, sample_docx_bytes)

    response = client.post(
        "/api/v1/export",
        json={
            "doc_id": uploaded["id"],
            "modifications": {
                "para_not_exist": "replacement",
            },
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["failed_ids"] == ["para_not_exist"]
    assert detail["applied_ids"] == []


def test_export_applies_modifications_to_docx(client, sample_docx_bytes):
    uploaded = upload_sample_doc(client, sample_docx_bytes)
    target_id = uploaded["paragraphs"][0]["id"]
    marker = "E2E_MARKER_20260207"

    response = client.post(
        "/api/v1/export",
        json={
            "doc_id": uploaded["id"],
            "modifications": {
                target_id: marker,
            },
        },
    )

    assert response.status_code == 200
    exported_doc = Document(BytesIO(response.content))
    non_empty = [p.text for p in exported_doc.paragraphs if p.text.strip()]
    assert marker in non_empty


def test_export_mixed_ids_does_not_pollute_cached_document(client, sample_docx_bytes):
    uploaded = upload_sample_doc(client, sample_docx_bytes)
    target_id = uploaded["paragraphs"][0]["id"]
    original_text = uploaded["paragraphs"][0]["text"]
    mutated_text = "MUTATED_SHOULD_NOT_PERSIST"

    response = client.post(
        "/api/v1/export",
        json={
            "doc_id": uploaded["id"],
            "modifications": {
                target_id: mutated_text,
                "para_not_exist": "invalid",
            },
        },
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["failed_ids"] == ["para_not_exist"]
    assert detail["applied_ids"] == []

    follow_up = client.get(f"/api/v1/export/{uploaded['id']}")
    assert follow_up.status_code == 200
    exported_doc = Document(BytesIO(follow_up.content))
    non_empty = [p.text for p in exported_doc.paragraphs if p.text.strip()]

    assert original_text in non_empty
    assert mutated_text not in non_empty


def test_rewrite_supports_sentence_unit_and_option_count(client, monkeypatch):
    class FakeRewriteService:
        def rewrite_text(self, text, mode, language, unit, option_count, max_retries=3):
            options = [f"{unit}-option-{idx}" for idx in range(1, option_count + 1)]
            sources = ["deepseek"] * option_count
            return {"options": options, "sources": sources}

    monkeypatch.setattr(rewrite_api, "get_deepseek_service", lambda: FakeRewriteService())

    response = client.post(
        "/api/v1/rewrite",
        json={
            "text": "This is one sentence.",
            "mode": "ai_detection",
            "language": "en",
            "unit": "sentence",
            "option_count": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["unit"] == "sentence"
    assert len(payload["options"]) == 2
    assert payload["meta"][0]["source"] == "deepseek"
