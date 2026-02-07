"""
改写API端点
"""

from fastapi import APIRouter, HTTPException
from app.models.rewrite import RewriteRequest, RewriteResponse
from app.services.deepseek import get_deepseek_service

router = APIRouter()


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    """
    改写文本
    
    Args:
        request: 改写请求
        
    Returns:
        改写响应（包含3个改写选项）
        
    Raises:
        HTTPException: 改写失败
    """
    try:
        # 获取DeepSeek服务
        deepseek_service = get_deepseek_service()
        
        # 调用改写服务
        rewrite_result = deepseek_service.rewrite_text(
            text=request.text,
            mode=request.mode,
            language=request.language,
            unit=request.unit,
            option_count=request.option_count,
        )
        
        return RewriteResponse(
            success=True,
            message="改写成功",
            options=rewrite_result["options"],
            mode=request.mode,
            language=request.language,
            unit=request.unit,
            meta=[{"source": source} for source in rewrite_result["sources"]],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"改写失败: {str(e)}")

