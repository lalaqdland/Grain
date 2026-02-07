from app.services import deepseek as deepseek_module


def _build_service(monkeypatch, use_marian_mt: bool, marian_option: str | None):
    service = deepseek_module.DeepSeekService.__new__(deepseek_module.DeepSeekService)
    monkeypatch.setattr(deepseek_module.settings, "use_marian_mt", use_marian_mt)
    monkeypatch.setattr(
        service,
        "_rewrite_with_deepseek",
        lambda text, mode, language, unit, option_count, max_retries: ["d1", "d2", "d3"],
    )
    monkeypatch.setattr(service, "_try_marian_option", lambda text: marian_option)
    return service


def test_english_ai_detection_includes_marian_candidate_when_enabled(monkeypatch):
    service = _build_service(monkeypatch, use_marian_mt=True, marian_option="marian_noise")

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["sources"].count("marian") >= 1
    assert "marian_noise" in result["options"]


def test_english_ai_detection_uses_all_deepseek_when_marian_disabled(monkeypatch):
    service = _build_service(monkeypatch, use_marian_mt=False, marian_option="marian_noise")

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["sources"] == ["deepseek", "deepseek", "deepseek"]
    assert result["options"] == ["d1", "d2", "d3"]

