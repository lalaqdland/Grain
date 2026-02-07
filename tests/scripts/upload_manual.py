"""
测试文件上传API
"""

import requests
import json
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8001"

def test_health():
    """测试健康检查端点"""
    print("\n=== 测试健康检查端点 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_api_info():
    """测试API信息端点"""
    print("\n=== 测试API信息端点 ===")
    response = requests.get(f"{BASE_URL}/api/v1/info")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_upload_no_file():
    """测试上传端点（无文件）"""
    print("\n=== 测试上传端点（无文件）===")
    response = requests.post(f"{BASE_URL}/api/v1/upload")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 422  # 应该返回422（验证错误）

def test_upload_wrong_format():
    """测试上传端点（错误格式）"""
    print("\n=== 测试上传端点（错误格式）===")
    # 创建一个临时的txt文件
    test_file = Path("test.txt")
    test_file.write_text("This is a test file")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400  # 应该返回400（格式错误）
    finally:
        test_file.unlink()

def test_upload_valid_docx():
    """测试上传端点（有效的.docx文件）"""
    print("\n=== 测试上传端点（有效的.docx文件）===")
    
    # 查找storage/temp目录中的测试文件
    storage_path = Path("storage/temp")
    docx_files = list(storage_path.glob("*.docx"))
    
    if not docx_files:
        print("❌ 未找到测试用的.docx文件")
        print(f"请在 {storage_path} 目录中放置一个测试用的.docx文件")
        return False
    
    test_file = docx_files[0]
    print(f"使用测试文件: {test_file.name}")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 验证响应结构
            assert result["success"] == True
            assert "data" in result
            assert "id" in result["data"]
            assert "paragraphs" in result["data"]
            
            print(f"\n✅ 文档上传成功！")
            print(f"文档ID: {result['data']['id']}")
            print(f"文件名: {result['data']['filename']}")
            print(f"段落数: {result['data']['total_paragraphs']}")
            print(f"\n前3个段落:")
            for i, para in enumerate(result['data']['paragraphs'][:3], 1):
                print(f"{i}. {para['text'][:50]}...")
            
            return True
        else:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Grain API 测试")
    print("=" * 60)
    
    results = {
        "健康检查": test_health(),
        "API信息": test_api_info(),
        "上传端点（无文件）": test_upload_no_file(),
        "上传端点（错误格式）": test_upload_wrong_format(),
        "上传端点（有效文件）": test_upload_valid_docx(),
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")

if __name__ == "__main__":
    main()

