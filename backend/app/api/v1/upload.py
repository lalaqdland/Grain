"""
文件上传API端点
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.document import DocumentUploadResponse, DocumentInfo, ParagraphInfo
from app.core.xml_processor import XMLProcessor, register_processor
from app.core.document_registry import register_document, get_document as get_registered_document
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
    if not file.filename or not file.filename.lower().endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="❌ 仅支持 .docx 格式\n\n为了保证完美的排版格式，请在 Word 中将文件'另存为' .docx 格式后再上传"
        )
    
    # 2. 验证文件大小
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"❌ 文件过大\n最大支持 {settings.max_upload_size / 1024 / 1024:.0f}MB，您的文件是 {file_size / 1024 / 1024:.1f}MB"
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
        
        # 5. 创建XML处理器并提取骨架（上传展示和导出统一使用同一套段落ID）
        xml_processor = XMLProcessor(str(temp_file_path))
        skeleton = xml_processor.extract_skeleton()
        register_processor(doc_id, xml_processor)
        
        # 6. 构建响应
        paragraphs = [
            ParagraphInfo(
                id=p["id"],
                text=p["text"],
                style=p["style"],
                is_modified=False,
                original_text=None,
            )
            for p in skeleton["paragraphs"]
        ]
        
        document_info = DocumentInfo(
            id=doc_id,
            filename=file.filename,
            paragraphs=paragraphs,
            total_paragraphs=skeleton["total_paragraphs"]
        )
        register_document(document_info)
        
        return DocumentUploadResponse(
            success=True,
            message="文档上传成功",
            data=document_info
        )
        
    except Exception as e:
        # 清理临时文件
        if temp_file_path.exists():
            temp_file_path.unlink()
        
        # 友好的错误提示
        error_msg = str(e)
        if "无法解析文档" in error_msg or "暂不支持" in error_msg:
            detail = f"❌ 文档解析失败\n{error_msg}"
        else:
            detail = f"❌ 文档处理失败\n{error_msg}\n请确保文件未损坏"
        
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@router.get("/upload/documents/{doc_id}", response_model=DocumentUploadResponse)
async def get_document_detail(doc_id: str):
    """
    获取文档信息
    
    Args:
        doc_id: 文档ID
        
    Returns:
        文档信息
    """
    try:
        document_info = get_registered_document(doc_id)
        return DocumentUploadResponse(
            success=True,
            message="文档获取成功",
            data=document_info,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

