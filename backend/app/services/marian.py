"""
MarianMT 回译服务（En -> De -> En）
"""

import importlib.util
from typing import Any
from config import get_settings

settings = get_settings()


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

        try:
            from transformers import MarianMTModel, MarianTokenizer
        except Exception as exc:
            raise RuntimeError(
                "MarianMT未安装，请安装transformers/torch/sentencepiece后再启用USE_MARIAN_MT"
            ) from exc

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
    }
