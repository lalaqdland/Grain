"""
MarianMT 回译服务（En -> De -> En）
"""

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
