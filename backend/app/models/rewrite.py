"""
改写请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class RewriteOptionMeta(BaseModel):
    """单个候选项元信息"""
    source: Literal["deepseek", "marian"] = Field(..., description="候选来源")


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

