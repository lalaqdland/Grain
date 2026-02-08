"""
改写Prompt库
"""

# 降重模式Prompt（中文）
PLAGIARISM_FIX_PROMPT_ZH = """你是一位专业的学术写作助手。请对以下文本进行改写，目标是降低查重率，同时保持学术性和专业性。

改写要求：
1. 使用同义词替换关键词
2. 调整句式结构（主动/被动语态转换、长短句重组）
3. 适当扩写，增加学术性表述
4. 保持原文的核心观点和逻辑
5. 确保语言流畅自然，符合学术规范
6. {unit_instruction}

原文：
{text}

请提供{option_count}个不同的改写版本，每个版本用"---VERSION---"分隔。只输出改写后的文本，不要添加任何解释或标注。"""

# 降重模式Prompt（英文）
PLAGIARISM_FIX_PROMPT_EN = """You are a professional academic writing assistant. Please rewrite the following text to reduce plagiarism detection while maintaining academic quality.

Requirements:
1. Use synonyms to replace key terms
2. Restructure sentences (active/passive voice, sentence length variation)
3. Expand appropriately with academic expressions
4. Maintain the core arguments and logic
5. Ensure fluent and natural academic language
6. {unit_instruction}

Original text:
{text}

Please provide {option_count} different rewritten versions, separated by "---VERSION---". Output only the rewritten text without any explanations or annotations."""

# 降AI模式Prompt（中文）
AI_DETECTION_FIX_PROMPT_ZH = """你是一位专业的人性化写作助手。请对以下文本进行改写，目标是降低AI检测率，让文本更像人类写作。

改写要求：
1. 增加语言的随机性和多样性（熵增）
2. 使用更口语化、自然的表达
3. 适当使用短句，避免过于工整的结构
4. 加入一些人类写作的特点（如轻微的语气词、过渡词）
5. 保持内容的准确性和完整性
6. {unit_instruction}

原文：
{text}

请提供{option_count}个不同的改写版本，每个版本用"---VERSION---"分隔。只输出改写后的文本，不要添加任何解释或标注。"""

# 降AI模式Prompt（英文）
AI_DETECTION_FIX_PROMPT_EN = """You are a professional humanization writing assistant. Please rewrite the following text to reduce AI detection and make it sound more human-written.

Requirements:
1. Increase language randomness and diversity (entropy increase)
2. Use more colloquial and natural expressions
3. Use shorter sentences appropriately, avoid overly structured patterns
4. Add human writing characteristics (e.g., slight tone words, transitions)
5. Maintain content accuracy and completeness
6. {unit_instruction}

Original text:
{text}

Please provide {option_count} different rewritten versions, separated by "---VERSION---". Output only the rewritten text without any explanations or annotations."""


def _get_unit_instruction(language: str, unit: str) -> str:
    if language == "zh":
        if unit == "sentence":
            return "仅改写该句，保持句外上下文不被改动，不要扩成整段。"
        return "以段落为单位改写，允许句间重组，但不要改变段落核心含义。"

    if unit == "sentence":
        return "Rewrite only this sentence and avoid spilling changes into surrounding context."
    return "Rewrite at paragraph level. You may reorganize sentence structure but keep core meaning."


def get_prompt(mode: str, language: str, text: str, unit: str = "paragraph", option_count: int = 3) -> str:
    """
    获取对应的Prompt。
    """
    prompt_map = {
        ("plagiarism", "zh"): PLAGIARISM_FIX_PROMPT_ZH,
        ("plagiarism", "en"): PLAGIARISM_FIX_PROMPT_EN,
        ("ai_detection", "zh"): AI_DETECTION_FIX_PROMPT_ZH,
        ("ai_detection", "en"): AI_DETECTION_FIX_PROMPT_EN,
    }

    prompt_template = prompt_map.get((mode, language))
    if not prompt_template:
        raise ValueError(f"不支持的模式或语言: mode={mode}, language={language}")

    return prompt_template.format(
        text=text,
        unit_instruction=_get_unit_instruction(language, unit),
        option_count=option_count,
    )

