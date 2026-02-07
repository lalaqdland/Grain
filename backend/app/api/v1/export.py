"""
文档导出API端点
"""

import os
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
from app.core.xml_processor import get_processor
from config import get_settings

router = APIRouter()
settings = get_settings()


class ExportRequest(BaseModel):
    """导出请求"""
    doc_id: str
    modifications: Dict[str, str]  # 段落ID到新文本的映射


def _build_output_path() -> tuple[str, str]:
    """生成导出文件名与输出路径。"""
    output_filename = f"modified_{uuid.uuid4().hex[:8]}.docx"
    output_dir = settings.temp_storage_path
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    return output_filename, output_path


@router.post("/export")
async def export_document(request: ExportRequest):
    """
    导出修改后的文档
    
    Args:
        request: 导出请求
        
    Returns:
        文件下载响应
        
    Raises:
        HTTPException: 导出失败
    """
    try:
        # 获取文档处理器
        processor = get_processor(request.doc_id)
        
        # 应用修改
        apply_result = processor.apply_modifications(request.modifications)
        if apply_result["failed_ids"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "部分段落ID不存在，导出已中止",
                    "failed_ids": apply_result["failed_ids"],
                    "applied_ids": apply_result["applied_ids"],
                },
            )
        
        # 生成输出文件路径
        output_filename, output_path = _build_output_path()
        
        # 保存文档
        processor.save_document(output_path)
        
        # 返回文件
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/export/{doc_id}")
async def export_document_get(doc_id: str):
    """
    导出文档（GET方法，用于简单导出）
    
    Args:
        doc_id: 文档ID
        
    Returns:
        文件下载响应
        
    Raises:
        HTTPException: 导出失败
    """
    try:
        # 获取文档处理器
        processor = get_processor(doc_id)
        
        # 生成输出文件路径
        output_filename, output_path = _build_output_path()
        
        # 保存文档（不做修改，直接导出当前状态）
        processor.save_document(output_path)
        
        # 返回文件
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

