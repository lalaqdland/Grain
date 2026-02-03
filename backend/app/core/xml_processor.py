"""
XML骨架处理器 - 用于保留Word文档格式
"""

import os
import uuid
from typing import Dict, List, Any
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from lxml import etree


class XMLProcessor:
    """XML骨架处理器"""
    
    def __init__(self, file_path: str):
        """
        初始化处理器
        
        Args:
            file_path: .docx文件路径
        """
        self.file_path = file_path
        self.document = Document(file_path)
        self.skeleton = {}  # 存储XML骨架
        self.paragraph_map = {}  # 段落ID到段落对象的映射
        
    def extract_skeleton(self) -> Dict[str, Any]:
        """
        提取XML骨架和段落索引
        
        Returns:
            包含骨架信息的字典
        """
        paragraphs_info = []
        
        for idx, para in enumerate(self.document.paragraphs):
            # 跳过空段落
            if not para.text.strip():
                continue
            
            # 生成唯一ID
            para_id = f"para_{uuid.uuid4().hex[:12]}"
            
            # 保存段落对象引用
            self.paragraph_map[para_id] = para
            
            # 提取段落信息
            para_info = {
                "id": para_id,
                "text": para.text,
                "style": para.style.name if para.style else "Normal",
                "index": idx
            }
            
            paragraphs_info.append(para_info)
        
        self.skeleton = {
            "file_path": self.file_path,
            "paragraphs": paragraphs_info,
            "total_paragraphs": len(paragraphs_info)
        }
        
        return self.skeleton
    
    def replace_paragraph_text(self, para_id: str, new_text: str) -> bool:
        """
        替换段落文本（保留格式）
        
        Args:
            para_id: 段落ID
            new_text: 新文本
            
        Returns:
            是否成功
        """
        if para_id not in self.paragraph_map:
            return False
        
        para = self.paragraph_map[para_id]
        
        # 保留原有格式，只替换文本
        # 清空段落内容
        for run in para.runs:
            run.text = ""
        
        # 如果段落有runs，使用第一个run的格式
        if para.runs:
            para.runs[0].text = new_text
        else:
            # 如果没有runs，添加新的run
            para.add_run(new_text)
        
        return True
    
    def save_document(self, output_path: str) -> str:
        """
        保存修改后的文档
        
        Args:
            output_path: 输出路径
            
        Returns:
            保存的文件路径
        """
        self.document.save(output_path)
        return output_path
    
    def apply_modifications(self, modifications: Dict[str, str]) -> None:
        """
        批量应用修改
        
        Args:
            modifications: 段落ID到新文本的映射
        """
        for para_id, new_text in modifications.items():
            self.replace_paragraph_text(para_id, new_text)


# 全局存储：文档ID到XMLProcessor的映射
_document_processors: Dict[str, XMLProcessor] = {}


def get_processor(doc_id: str) -> XMLProcessor:
    """
    获取文档处理器
    
    Args:
        doc_id: 文档ID
        
    Returns:
        XMLProcessor实例
        
    Raises:
        ValueError: 文档不存在
    """
    if doc_id not in _document_processors:
        raise ValueError(f"文档不存在: {doc_id}")
    return _document_processors[doc_id]


def register_processor(doc_id: str, processor: XMLProcessor) -> None:
    """
    注册文档处理器
    
    Args:
        doc_id: 文档ID
        processor: XMLProcessor实例
    """
    _document_processors[doc_id] = processor


def remove_processor(doc_id: str) -> None:
    """
    移除文档处理器
    
    Args:
        doc_id: 文档ID
    """
    if doc_id in _document_processors:
        del _document_processors[doc_id]

