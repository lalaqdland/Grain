"""
改写请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class RewriteRequest(BaseModel):
    """改写请求"""
    text: str = Field(..., description="需要改写的文本")
    mode: Literal["plagiarism", "ai_detection"] = Field(..., description="改写模式：降重或降AI")
    language: Literal["zh", "en"] = Field(..., description="文本语言：中文或英文")


class RewriteResponse(BaseModel):
    """改写响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    options: List[str] = Field(default_factory=list, description="改写选项列表（3个）")
    mode: str = Field(..., description="使用的改写模式")
    language: str = Field(..., description="文本语言")

