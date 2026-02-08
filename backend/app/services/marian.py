"""
MarianMT 回译服务（En -> De -> En）
"""

import importlib.util
from threading import Lock
from time import perf_counter
from typing import Any
from config import get_settings

settings = get_settings()

_runtime_lock = Lock()
_runtime_metrics: dict[str, Any] = {
    "model_loaded": False,
    "first_load_duration_ms": None,
    "load_attempts": 0,
    "load_failures": 0,
    "generation_attempts": 0,
    "generation_failures": 0,
    "last_generation_error": None,
}


def _snapshot_runtime_metrics() -> dict[str, Any]:
    with _runtime_lock:
        attempts = int(_runtime_metrics["generation_attempts"])
        failures = int(_runtime_metrics["generation_failures"])
        failure_rate = failures / attempts if attempts else 0.0
        return {
            "model_loaded": bool(_runtime_metrics["model_loaded"]),
            "first_load_duration_ms": _runtime_metrics["first_load_duration_ms"],
            "load_attempts": int(_runtime_metrics["load_attempts"]),
            "load_failures": int(_runtime_metrics["load_failures"]),
            "generation_attempts": attempts,
            "generation_failures": failures,
            "generation_failure_rate": round(failure_rate, 4),
            "last_generation_error": _runtime_metrics["last_generation_error"],
        }


def _record_load_attempt() -> None:
    with _runtime_lock:
        _runtime_metrics["load_attempts"] += 1


def _record_load_failure() -> None:
    with _runtime_lock:
        _runtime_metrics["load_failures"] += 1


def _record_load_success(duration_ms: float) -> None:
    with _runtime_lock:
        _runtime_metrics["model_loaded"] = True
        if _runtime_metrics["first_load_duration_ms"] is None:
            _runtime_metrics["first_load_duration_ms"] = round(duration_ms, 2)


def record_marian_generation_attempt() -> None:
    """记录一次 Marian 生成尝试。"""
    with _runtime_lock:
        _runtime_metrics["generation_attempts"] += 1


def record_marian_generation_failure(error: Exception | str) -> None:
    """记录一次 Marian 生成失败。"""
    with _runtime_lock:
        _runtime_metrics["generation_failures"] += 1
        _runtime_metrics["last_generation_error"] = str(error)


def reset_marian_runtime_metrics() -> None:
    """重置 Marian 运行态指标（测试场景）。"""
    with _runtime_lock:
        _runtime_metrics["model_loaded"] = False
        _runtime_metrics["first_load_duration_ms"] = None
        _runtime_metrics["load_attempts"] = 0
        _runtime_metrics["load_failures"] = 0
        _runtime_metrics["generation_attempts"] = 0
        _runtime_metrics["generation_failures"] = 0
        _runtime_metrics["last_generation_error"] = None


class MarianService:
    """MarianMT回译服务。"""

    def __init__(self):
        self._loaded = False
        self._tokenizer_en_de: Any = None
        self._model_en_de: Any = None
        self._tokenizer_de_en: Any = None
        self._model_de_en: Any = None

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        _record_load_attempt()
        load_started_at = perf_counter()

        try:
            from transformers import MarianMTModel, MarianTokenizer
        except Exception as exc:
            _record_load_failure()
            raise RuntimeError(
                "MarianMT未安装，请安装transformers/torch/sentencepiece后再启用USE_MARIAN_MT"
            ) from exc

        try:
            cache_dir = settings.marian_cache_dir or None
            self._tokenizer_en_de = MarianTokenizer.from_pretrained(
                settings.marian_en_de_model,
                cache_dir=cache_dir,
            )
            self._model_en_de = MarianMTModel.from_pretrained(
                settings.marian_en_de_model,
                cache_dir=cache_dir,
            )
            self._tokenizer_de_en = MarianTokenizer.from_pretrained(
                settings.marian_de_en_model,
                cache_dir=cache_dir,
            )
            self._model_de_en = MarianMTModel.from_pretrained(
                settings.marian_de_en_model,
                cache_dir=cache_dir,
            )
            self._loaded = True
            _record_load_success((perf_counter() - load_started_at) * 1000)
        except Exception:
            _record_load_failure()
            raise

    @staticmethod
    def _translate(text: str, tokenizer: Any, model: Any) -> str:
        batch = tokenizer([text], return_tensors="pt", truncation=True, max_length=512, padding=True)
        generated = model.generate(**batch, max_length=512, num_beams=4)
        return tokenizer.decode(generated[0], skip_special_tokens=True)

    def back_translate_en(self, text: str) -> str:
        """
        英文回译：En -> De -> En。
        """
        if not text.strip():
            return text

        self._ensure_loaded()

        german = self._translate(text, self._tokenizer_en_de, self._model_en_de)
        english = self._translate(german, self._tokenizer_de_en, self._model_de_en)
        return english.strip() or text


_marian_service: MarianService | None = None


def get_marian_service() -> MarianService:
    """获取Marian服务单例。"""
    global _marian_service
    if _marian_service is None:
        _marian_service = MarianService()
    return _marian_service


def probe_marian_dependencies() -> dict[str, bool]:
    """探测 Marian 依赖可用性（不触发模型加载）。"""
    return {
        "transformers": importlib.util.find_spec("transformers") is not None,
        "torch": importlib.util.find_spec("torch") is not None,
        "sentencepiece": importlib.util.find_spec("sentencepiece") is not None,
    }


def get_marian_runtime_info() -> dict[str, Any]:
    """获取 Marian 运行态信息。"""
    dependencies = probe_marian_dependencies()
    dependency_ready = all(dependencies.values())
    enabled = bool(settings.use_marian_mt)
    metrics = _snapshot_runtime_metrics()

    missing_dependencies = [name for name, ready in dependencies.items() if not ready]
    if not enabled:
        status = "disabled"
        reason = "USE_MARIAN_MT=false"
    elif dependency_ready:
        status = "enabled"
        reason = None
    else:
        status = "degraded"
        reason = f"missing_dependencies:{','.join(missing_dependencies)}"

    return {
        "enabled": enabled,
        "dependency_ready": dependency_ready,
        "dependencies": dependencies,
        "status": status,
        "reason": reason,
        "model_loaded": metrics["model_loaded"],
        "first_load_duration_ms": metrics["first_load_duration_ms"],
        "load_attempts": metrics["load_attempts"],
        "load_failures": metrics["load_failures"],
        "generation_attempts": metrics["generation_attempts"],
        "generation_failures": metrics["generation_failures"],
        "generation_failure_rate": metrics["generation_failure_rate"],
        "last_generation_error": metrics["last_generation_error"],
    }
