"""
文件上传API端点
"""

import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.models.document import DocumentUploadResponse, DocumentInfo, ParagraphInfo
from app.core.docx_parser import DocxParser
from config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传Word文档
    
    Args:
        file: 上传的.docx文件
        
    Returns:
        文档上传响应，包含文档信息
        
    Raises:
        HTTPException: 文件格式错误或文件过大
    """
    
    # 1. 验证文件格式
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="文件格式不支持，仅支持.docx格式"
        )
    
    # 2. 验证文件大小
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持{settings.max_upload_size / 1024 / 1024}MB"
        )
    
    # 3. 生成唯一文档ID和文件名
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    temp_filename = f"{doc_id}_{file.filename}"
    
    # 4. 保存到临时目录
    temp_dir = Path(settings.temp_storage_path)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_file_path = temp_dir / temp_filename
    
    try:
        # 写入文件
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        # 5. 解析文档
        parser = DocxParser(str(temp_file_path))
        parsed_data = parser.parse()
        
        # 6. 构建响应
        paragraphs = [ParagraphInfo(**p) for p in parsed_data["paragraphs"]]
        
        document_info = DocumentInfo(
            id=doc_id,
            filename=file.filename,
            paragraphs=paragraphs,
            total_paragraphs=parsed_data["total_paragraphs"]
        )
        
        return DocumentUploadResponse(
            success=True,
            message="文档上传成功",
            data=document_info
        )
        
    except Exception as e:
        # 清理临时文件
        if temp_file_path.exists():
            temp_file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"文档解析失败: {str(e)}"
        )


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    获取文档信息
    
    Args:
        doc_id: 文档ID
        
    Returns:
        文档信息
    """
    # TODO: 实现文档信息获取（从缓存或数据库）
    return JSONResponse(
        status_code=501,
        content={"message": "功能开发中"}
    )

