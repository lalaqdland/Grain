"""
文档导出API端点
"""

import logging
import os
import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
from app.core.xml_processor import get_processor
from app.core.export_observability import get_export_failure_stats_store
from config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


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
            try:
                get_export_failure_stats_store().record_failure(
                    doc_id=request.doc_id,
                    failed_ids=apply_result["failed_ids"],
                )
            except Exception:
                logger.warning(
                    "failed to record export failure stats",
                    extra={
                        "doc_id": request.doc_id,
                        "failed_ids_count": len(apply_result["failed_ids"]),
                    },
                    exc_info=True,
                )
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "部分段落ID不存在，导出已中止",
                    "failed_ids": apply_result["failed_ids"],
                    # 严格原子语义：失败时不落地任何修改。
                    "applied_ids": [],
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


@router.get("/export/stats")
async def get_export_failure_stats(
    window_minutes: int = Query(default=60, ge=1, le=43200),
    doc_id: str | None = Query(default=None),
    top_n: int = Query(default=20, ge=1, le=100),
):
    """查询导出失败统计。"""
    try:
        return get_export_failure_stats_store().query(
            window_minutes=window_minutes,
            doc_id=doc_id,
            top_n=top_n,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"导出统计查询失败: {str(exc)}") from exc


@router.get("/export/stats/storage")
async def get_export_failure_stats_storage():
    """查询导出统计SQLite存储体积与风险级别。"""
    try:
        return get_export_failure_stats_store().get_storage_metrics(
            warn_bytes=settings.export_stats_db_warn_bytes,
            critical_bytes=settings.export_stats_db_critical_bytes,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"导出统计存储指标查询失败: {str(exc)}") from exc


@router.post("/export/stats/prune")
async def prune_export_failure_stats(
    retention_days: int = Query(default=30, ge=1, le=365),
):
    """
    清理过期的导出失败统计事件。

    - 默认保留 30 天数据
    - 返回清理前后的事件数量
    """
    try:
        return get_export_failure_stats_store().prune_old_events(
            retention_days=retention_days,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"清理导出统计失败: {str(exc)}") from exc


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

