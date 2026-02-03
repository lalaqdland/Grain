"""
测试改写API
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_rewrite_api():
    """测试改写API"""
    
    print("=" * 60)
    print("测试改写API")
    print("=" * 60)
    
    # 测试数据
    test_cases = [
        {
            "name": "中文降重模式",
            "data": {
                "text": "人工智能技术在近年来取得了显著的进展，特别是在自然语言处理领域。",
                "mode": "plagiarism",
                "language": "zh"
            }
        },
        {
            "name": "中文降AI模式",
            "data": {
                "text": "深度学习模型通过多层神经网络结构，能够自动学习数据中的特征表示。",
                "mode": "ai_detection",
                "language": "zh"
            }
        },
        {
            "name": "英文降重模式",
            "data": {
                "text": "Artificial intelligence has made significant progress in recent years.",
                "mode": "plagiarism",
                "language": "en"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/rewrite",
                json=test_case['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 状态: {response.status_code}")
                print(f"✅ 成功: {result.get('success')}")
                print(f"✅ 消息: {result.get('message')}")
                print(f"✅ 模式: {result.get('mode')}")
                print(f"✅ 语言: {result.get('language')}")
                print(f"\n原文:")
                print(f"  {test_case['data']['text']}")
                print(f"\n改写选项:")
                for idx, option in enumerate(result.get('options', []), 1):
                    print(f"  {idx}. {option}")
            else:
                print(f"❌ 状态: {response.status_code}")
                print(f"❌ 错误: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 错误: 无法连接到服务器")
            print("   请确保后端服务已启动: uvicorn main:app --reload --host 0.0.0.0 --port 8001")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_rewrite_api()

