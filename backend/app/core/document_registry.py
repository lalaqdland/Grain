"""
文档元数据内存注册表
"""

from typing import Dict

from app.models.document import DocumentInfo

_documents: Dict[str, DocumentInfo] = {}


def register_document(document: DocumentInfo) -> None:
    """注册文档元数据。"""
    _documents[document.id] = document


def get_document(doc_id: str) -> DocumentInfo:
    """获取文档元数据。"""
    if doc_id not in _documents:
        raise ValueError(f"文档不存在: {doc_id}")
    return _documents[doc_id]


def remove_document(doc_id: str) -> None:
    """移除文档元数据。"""
    if doc_id in _documents:
        del _documents[doc_id]


def clear_documents() -> None:
    """清空文档元数据（测试场景使用）。"""
    _documents.clear()
