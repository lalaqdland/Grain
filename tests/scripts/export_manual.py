"""
测试文档导出功能
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8001"

def test_export_workflow():
    """测试完整的上传-改写-导出流程"""
    print("=" * 60)
    print("测试完整工作流：上传 -> 改写 -> 导出")
    print("=" * 60)
    
    # 1. 上传文档
    print("\n=== 步骤1: 上传文档 ===")
    test_file = Path("../test_files/test_document.docx")
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    with open(test_file, "rb") as f:
        files = {"file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ 上传失败: {response.status_code}")
        return False
    
    upload_result = response.json()
    doc_id = upload_result['data']['id']
    print(f"✅ 上传成功！文档ID: {doc_id}")
    print(f"   段落数: {upload_result['data']['total_paragraphs']}")
    
    # 2. 改写第一个段落
    print("\n=== 步骤2: 改写段落 ===")
    first_para = upload_result['data']['paragraphs'][0]
    print(f"原文: {first_para['text'][:50]}...")
    
    rewrite_payload = {
        "text": first_para['text'],
        "mode": "plagiarism",
        "language": "zh"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/rewrite", json=rewrite_payload)
    
    if response.status_code != 200:
        print(f"❌ 改写失败: {response.status_code}")
        return False
    
    rewrite_result = response.json()
    new_text = rewrite_result['options'][0]
    print(f"✅ 改写成功！")
    print(f"新文本: {new_text[:50]}...")
    
    # 3. 导出文档（带修改）
    print("\n=== 步骤3: 导出修改后的文档 ===")
    export_payload = {
        "doc_id": doc_id,
        "modifications": {
            first_para['id']: new_text
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/export", json=export_payload)
    
    if response.status_code != 200:
        print(f"❌ 导出失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    # 保存导出的文件
    output_file = Path("../storage/temp/exported_test.docx")
    output_file.write_bytes(response.content)
    
    print(f"✅ 导出成功！")
    print(f"   文件大小: {len(response.content)} 字节")
    print(f"   保存位置: {output_file}")
    
    return True

def test_export_without_modifications():
    """测试导出未修改的文档"""
    print("\n" + "=" * 60)
    print("测试导出未修改的文档")
    print("=" * 60)
    
    # 上传文档
    test_file = Path("../test_files/test_document.docx")
    
    with open(test_file, "rb") as f:
        files = {"file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    
    doc_id = response.json()['data']['id']
    print(f"文档ID: {doc_id}")
    
    # 导出（不带修改）
    response = requests.get(f"{BASE_URL}/api/v1/export/{doc_id}")
    
    if response.status_code != 200:
        print(f"❌ 导出失败: {response.status_code}")
        return False
    
    output_file = Path("../storage/temp/exported_original.docx")
    output_file.write_bytes(response.content)
    
    print(f"✅ 导出成功！")
    print(f"   文件大小: {len(response.content)} 字节")
    print(f"   保存位置: {output_file}")
    
    return True

def main():
    """运行所有测试"""
    results = {
        "完整工作流（上传-改写-导出）": test_export_workflow(),
        "导出未修改文档": test_export_without_modifications(),
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

