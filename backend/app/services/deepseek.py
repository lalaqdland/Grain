"""
DeepSeek API服务
"""

import os
from typing import List
from openai import OpenAI
from config import get_settings
from app.prompts.rewrite_prompts import get_prompt

settings = get_settings()


class DeepSeekService:
    """DeepSeek API服务类"""
    
    def __init__(self):
        """初始化DeepSeek客户端"""
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置，请在.env文件中设置DEEPSEEK_API_KEY")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.deepseek_base_url
        )
        self.model = settings.deepseek_model
    
    def rewrite_text(
        self, 
        text: str, 
        mode: str, 
        language: str,
        max_retries: int = 3
    ) -> List[str]:
        """
        改写文本
        
        Args:
            text: 原文
            mode: 改写模式（plagiarism或ai_detection）
            language: 语言（zh或en）
            max_retries: 最大重试次数
            
        Returns:
            改写选项列表（3个）
            
        Raises:
            Exception: API调用失败
        """
        # 获取对应的Prompt
        prompt = get_prompt(mode, language, text)
        
        # 调用DeepSeek API
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位专业的写作助手，擅长文本改写和优化。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.8,  # 增加随机性
                    max_tokens=2000,
                    top_p=0.95
                )
                
                # 解析响应
                content = response.choices[0].message.content
                options = self._parse_response(content)
                
                # 确保返回3个选项
                if len(options) >= 3:
                    return options[:3]
                elif len(options) > 0:
                    # 如果少于3个，用第一个选项填充
                    while len(options) < 3:
                        options.append(options[0])
                    return options
                else:
                    # 如果解析失败，重试
                    if attempt < max_retries - 1:
                        continue
                    else:
                        # 最后一次尝试失败，返回原文
                        return [text, text, text]
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception(f"DeepSeek API调用失败: {str(e)}")
        
        # 如果所有重试都失败，返回原文
        return [text, text, text]
    
    def _parse_response(self, content: str) -> List[str]:
        """
        解析API响应，提取改写选项
        
        Args:
            content: API返回的内容
            
        Returns:
            改写选项列表
        """
        # 按分隔符分割
        versions = content.split("---VERSION---")
        
        # 清理每个版本
        options = []
        for version in versions:
            cleaned = version.strip()
            if cleaned:
                options.append(cleaned)
        
        return options


# 创建全局实例
_deepseek_service = None


def get_deepseek_service() -> DeepSeekService:
    """
    获取DeepSeek服务单例
    
    Returns:
        DeepSeekService实例
    """
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service

