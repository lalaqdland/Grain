"""
改写请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class RewriteOptionMeta(BaseModel):
    """单个候选项元信息"""
    source: Literal["deepseek", "marian"] = Field(..., description="候选来源")


class MarianDiagnostics(BaseModel):
    """Marian 候选生成诊断信息。"""
    enabled: bool = Field(..., description="Marian 开关是否启用")
    eligible: bool = Field(..., description="请求是否满足 Marian 参与条件")
    attempted: bool = Field(..., description="是否已尝试调用 Marian")
    dependency_ready: bool = Field(..., description="Marian 依赖是否齐全")
    used: bool = Field(..., description="最终候选是否使用 Marian 结果")
    status: Literal[
        "used",
        "disabled",
        "not_eligible",
        "dependency_missing",
        "generation_failed",
        "no_effect",
    ] = Field(..., description="Marian 链路状态")
    reason: Optional[str] = Field(default=None, description="状态说明或失败原因")


class RewriteDiagnostics(BaseModel):
    """改写链路诊断信息。"""
    marian: MarianDiagnostics = Field(..., description="Marian 链路诊断")


class RewriteRequest(BaseModel):
    """改写请求"""
    text: str = Field(..., description="需要改写的文本")
    mode: Literal["plagiarism", "ai_detection"] = Field(..., description="改写模式：降重或降AI")
    language: Literal["zh", "en"] = Field(..., description="文本语言：中文或英文")
    unit: Literal["sentence", "paragraph"] = Field(default="paragraph", description="改写单元：句子或段落")
    option_count: int = Field(default=3, ge=2, le=3, description="候选数量，支持2或3")


class RewriteResponse(BaseModel):
    """改写响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    options: List[str] = Field(default_factory=list, description="改写选项列表")
    mode: str = Field(..., description="使用的改写模式")
    language: str = Field(..., description="文本语言")
    unit: Literal["sentence", "paragraph"] = Field(..., description="改写单元")
    meta: Optional[List[RewriteOptionMeta]] = Field(default=None, description="候选项元信息")
    diagnostics: Optional[RewriteDiagnostics] = Field(default=None, description="改写链路诊断")

