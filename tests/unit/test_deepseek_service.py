from app.services import deepseek as deepseek_module


def _build_service(
    monkeypatch,
    use_marian_mt: bool,
    dependency_ready: bool,
    marian_attempt: dict | None = None,
):
    service = deepseek_module.DeepSeekService.__new__(deepseek_module.DeepSeekService)
    monkeypatch.setattr(deepseek_module.settings, "use_marian_mt", use_marian_mt)
    monkeypatch.setattr(
        deepseek_module,
        "get_marian_runtime_info",
        lambda: {
            "enabled": use_marian_mt,
            "dependency_ready": dependency_ready,
            "dependencies": {
                "transformers": dependency_ready,
                "torch": dependency_ready,
                "sentencepiece": dependency_ready,
            },
            "status": (
                "enabled"
                if use_marian_mt and dependency_ready
                else "disabled"
                if not use_marian_mt
                else "degraded"
            ),
            "reason": (
                None
                if use_marian_mt and dependency_ready
                else "USE_MARIAN_MT=false"
                if not use_marian_mt
                else "missing_dependencies:transformers,torch,sentencepiece"
            ),
        },
    )
    monkeypatch.setattr(
        service,
        "_rewrite_with_deepseek",
        lambda text, mode, language, unit, option_count, max_retries: ["d1", "d2", "d3"],
    )
    monkeypatch.setattr(
        service,
        "_try_marian_option",
        lambda text: marian_attempt
        or {"candidate": None, "status": "no_effect", "reason": "candidate is empty or unchanged"},
    )
    return service


def test_english_ai_detection_includes_marian_candidate_when_enabled(monkeypatch):
    service = _build_service(
        monkeypatch,
        use_marian_mt=True,
        dependency_ready=True,
        marian_attempt={"candidate": "marian_noise", "status": "used", "reason": None},
    )

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["sources"].count("marian") >= 1
    assert "marian_noise" in result["options"]
    assert result["diagnostics"]["marian"]["status"] == "used"
    assert result["diagnostics"]["marian"]["used"] is True


def test_english_ai_detection_uses_all_deepseek_when_marian_disabled(monkeypatch):
    service = _build_service(
        monkeypatch,
        use_marian_mt=False,
        dependency_ready=False,
        marian_attempt={"candidate": "marian_noise", "status": "used", "reason": None},
    )

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["sources"] == ["deepseek", "deepseek", "deepseek"]
    assert result["options"] == ["d1", "d2", "d3"]
    assert result["diagnostics"]["marian"]["status"] == "disabled"
    assert result["diagnostics"]["marian"]["attempted"] is False


def test_english_ai_detection_marks_dependency_missing(monkeypatch):
    service = _build_service(
        monkeypatch,
        use_marian_mt=True,
        dependency_ready=False,
    )

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["diagnostics"]["marian"]["status"] == "dependency_missing"
    assert result["diagnostics"]["marian"]["attempted"] is False


def test_english_ai_detection_marks_no_effect(monkeypatch):
    service = _build_service(
        monkeypatch,
        use_marian_mt=True,
        dependency_ready=True,
        marian_attempt={
            "candidate": None,
            "status": "no_effect",
            "reason": "candidate is empty or unchanged",
        },
    )

    result = service.rewrite_text(
        text="This is a test sentence.",
        mode="ai_detection",
        language="en",
        unit="sentence",
        option_count=3,
    )

    assert result["diagnostics"]["marian"]["status"] == "no_effect"
    assert result["diagnostics"]["marian"]["attempted"] is True
    assert result["diagnostics"]["marian"]["used"] is False
