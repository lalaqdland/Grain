"""
测试Grain API的文件上传功能
"""
import requests
import json
from pathlib import Path

# API配置
API_BASE_URL = "http://localhost:8001"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/upload"

def test_upload_api():
    """测试文件上传API"""
    
    # 测试文件路径（需要一个真实的.docx文件）
    test_file_path = Path(__file__).parent / "test_files" / "test_document.docx"
    
    if not test_file_path.exists():
        print(f"❌ 测试文件不存在: {test_file_path}")
        print("请在 test_files 目录下放置一个名为 test_document.docx 的文件")
        return
    
    print(f"📄 测试文件: {test_file_path}")
    print(f"📡 上传到: {UPLOAD_ENDPOINT}")
    print("-" * 50)
    
    try:
        # 打开文件并上传
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        # 打印响应
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✅ 上传成功！")
            data = response.json()
            if data.get('success'):
                doc_info = data.get('data', {})
                print(f"\n📄 文档信息:")
                print(f"  - ID: {doc_info.get('id')}")
                print(f"  - 文件名: {doc_info.get('filename')}")
                print(f"  - 段落数: {doc_info.get('total_paragraphs')}")
                print(f"\n📝 前3个段落:")
                for i, para in enumerate(doc_info.get('paragraphs', [])[:3], 1):
                    print(f"  {i}. [{para.get('style')}] {para.get('text')[:50]}...")
        else:
            print(f"\n❌ 上传失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def test_health_check():
    """测试健康检查端点"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Grain API 测试")
    print("=" * 50)
    print()
    
    # 1. 健康检查
    print("1️⃣ 健康检查测试")
    print("-" * 50)
    test_health_check()
    print()
    
    # 2. 文件上传测试
    print("2️⃣ 文件上传测试")
    print("-" * 50)
    test_upload_api()
    print()
    
    print("=" * 50)
    print("🎉 测试完成")
    print("=" * 50)

