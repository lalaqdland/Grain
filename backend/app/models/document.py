"""
数据模型模块
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ParagraphInfo(BaseModel):
    """段落信息"""
    id: str = Field(..., description="段落唯一ID")
    text: str = Field(..., description="段落文本内容")
    style: str = Field(default="Normal", description="段落样式")
    is_modified: bool = Field(default=False, description="是否已修改")
    original_text: Optional[str] = Field(None, description="原始文本（用于撤销）")


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str = Field(..., description="文档唯一ID")
    filename: str = Field(..., description="文件名")
    paragraphs: List[ParagraphInfo] = Field(default_factory=list, description="段落列表")
    uploaded_at: datetime = Field(default_factory=datetime.now, description="上传时间")
    total_paragraphs: int = Field(default=0, description="总段落数")


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[DocumentInfo] = Field(None, description="文档信息")

