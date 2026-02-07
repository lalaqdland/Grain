"""
DeepSeek API服务
"""

from typing import Any, Dict, List
from openai import OpenAI
from config import get_settings
from app.prompts.rewrite_prompts import get_prompt
from app.services.marian import get_marian_runtime_info, get_marian_service

settings = get_settings()


class DeepSeekService:
    """DeepSeek API服务类"""

    def __init__(self):
        """初始化DeepSeek客户端"""
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置，请在.env文件中设置DEEPSEEK_API_KEY")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    def rewrite_text(
        self,
        text: str,
        mode: str,
        language: str,
        unit: str = "paragraph",
        option_count: int = 3,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        改写文本。

        Returns:
            {
                "options": ["...", "..."],
                "sources": ["deepseek", "marian"]
            }
        """
        option_count = max(2, min(option_count, 3))

        options = self._rewrite_with_deepseek(
            text=text,
            mode=mode,
            language=language,
            unit=unit,
            option_count=option_count,
            max_retries=max_retries,
        )
        sources = ["deepseek"] * len(options)

        runtime_info = get_marian_runtime_info()
        marian_eligible = mode == "ai_detection" and language == "en"
        marian_diagnostics = {
            "enabled": runtime_info["enabled"],
            "eligible": marian_eligible,
            "attempted": False,
            "dependency_ready": runtime_info["dependency_ready"],
            "used": False,
            "status": "not_eligible",
            "reason": "marian only applies to ai_detection/en requests",
        }

        # 英文降AI可选Marian噪声候选
        if marian_eligible:
            if not runtime_info["enabled"]:
                marian_diagnostics["status"] = "disabled"
                marian_diagnostics["reason"] = runtime_info["reason"]
            elif not runtime_info["dependency_ready"]:
                marian_diagnostics["status"] = "dependency_missing"
                marian_diagnostics["reason"] = runtime_info["reason"]
            else:
                marian_diagnostics["attempted"] = True
                marian_attempt = self._try_marian_option(text)
                marian_option = marian_attempt["candidate"]
                marian_diagnostics["status"] = marian_attempt["status"]
                marian_diagnostics["reason"] = marian_attempt["reason"]
                marian_diagnostics["used"] = bool(marian_option)

                if marian_option:
                    if options:
                        options[-1] = marian_option
                        sources[-1] = "marian"
                    else:
                        options = [marian_option]
                        sources = ["marian"]
        else:
            marian_diagnostics["dependency_ready"] = runtime_info["dependency_ready"]

        options, sources = self._normalize_options(text, options, sources, option_count)
        return {
            "options": options,
            "sources": sources,
            "diagnostics": {
                "marian": marian_diagnostics,
            },
        }

    def _try_marian_option(self, text: str) -> Dict[str, Any]:
        """尝试生成 Marian 候选，并返回详细状态。"""
        try:
            marian_service = get_marian_service()
            candidate = marian_service.back_translate_en(text)
            if candidate and candidate.strip() and candidate.strip() != text.strip():
                return {
                    "candidate": candidate.strip(),
                    "status": "used",
                    "reason": None,
                }
            return {
                "candidate": None,
                "status": "no_effect",
                "reason": "candidate is empty or unchanged",
            }
        except Exception as exc:
            return {
                "candidate": None,
                "status": "generation_failed",
                "reason": str(exc),
            }

    def _rewrite_with_deepseek(
        self,
        text: str,
        mode: str,
        language: str,
        unit: str,
        option_count: int,
        max_retries: int,
    ) -> List[str]:
        prompt = get_prompt(mode, language, text, unit=unit, option_count=option_count)

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位专业的写作助手，擅长文本改写和优化。",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.8,
                    max_tokens=2000,
                    top_p=0.95,
                )

                content = response.choices[0].message.content
                options = self._parse_response(content)
                if options:
                    return options

                if attempt < max_retries - 1:
                    continue

            except Exception as exc:
                if attempt < max_retries - 1:
                    continue
                raise Exception(f"DeepSeek API调用失败: {str(exc)}") from exc

        return [text]

    @staticmethod
    def _normalize_options(
        original_text: str,
        options: List[str],
        sources: List[str],
        option_count: int,
    ) -> tuple[List[str], List[str]]:
        cleaned_options = [opt.strip() for opt in options if opt and opt.strip()]
        cleaned_sources = sources[: len(cleaned_options)]

        if not cleaned_options:
            cleaned_options = [original_text]
            cleaned_sources = ["deepseek"]

        while len(cleaned_options) < option_count:
            cleaned_options.append(cleaned_options[0])
            cleaned_sources.append(cleaned_sources[0])

        return cleaned_options[:option_count], cleaned_sources[:option_count]

    @staticmethod
    def _parse_response(content: str | None) -> List[str]:
        if not content:
            return []

        versions = content.split("---VERSION---")
        options = []
        for version in versions:
            cleaned = version.strip()
            if cleaned:
                options.append(cleaned)
        return options


_deepseek_service = None


def get_deepseek_service() -> DeepSeekService:
    """获取DeepSeek服务单例"""
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service
