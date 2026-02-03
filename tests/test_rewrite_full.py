"""
完整测试改写功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_rewrite():
    """测试改写功能"""
    print("=" * 60)
    print("测试改写功能")
    print("=" * 60)
    
    # 测试文本
    test_text = "人工智能技术在近年来取得了显著的进展，深度学习算法的应用使得计算机能够处理更加复杂的任务。"
    
    # 测试降重模式（中文）
    print("\n=== 测试降重模式（中文）===")
    payload = {
        "text": test_text,
        "mode": "plagiarism",
        "language": "zh"
    }
    
    print(f"原文: {test_text}")
    print("请求改写...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/rewrite", json=payload)
    elapsed = time.time() - start_time
    
    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f}秒")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 改写成功！")
        print(f"生成了 {len(result['options'])} 个选项:\n")
        for i, option in enumerate(result['options'], 1):
            print(f"选项 {i}:")
            print(f"  {option}")
            print()
        return True
    else:
        print(f"❌ 改写失败")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return False

def test_rewrite_ai_mode():
    """测试降AI模式"""
    print("\n=== 测试降AI模式（中文）===")
    
    test_text = "根据数据分析结果显示，该方案具有较高的可行性和实用价值。"
    
    payload = {
        "text": test_text,
        "mode": "ai_detection",
        "language": "zh"
    }
    
    print(f"原文: {test_text}")
    print("请求改写...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/rewrite", json=payload)
    elapsed = time.time() - start_time
    
    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f}秒")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 改写成功！")
        print(f"生成了 {len(result['options'])} 个选项:\n")
        for i, option in enumerate(result['options'], 1):
            print(f"选项 {i}:")
            print(f"  {option}")
            print()
        return True
    else:
        print(f"❌ 改写失败")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return False

def test_rewrite_english():
    """测试英文改写"""
    print("\n=== 测试降重模式（英文）===")
    
    test_text = "Artificial intelligence has made significant progress in recent years."
    
    payload = {
        "text": test_text,
        "mode": "plagiarism",
        "language": "en"
    }
    
    print(f"原文: {test_text}")
    print("请求改写...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/rewrite", json=payload)
    elapsed = time.time() - start_time
    
    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f}秒")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 改写成功！")
        print(f"生成了 {len(result['options'])} 个选项:\n")
        for i, option in enumerate(result['options'], 1):
            print(f"选项 {i}:")
            print(f"  {option}")
            print()
        return True
    else:
        print(f"❌ 改写失败")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return False

def main():
    """运行所有测试"""
    results = {
        "降重模式（中文）": test_rewrite(),
        "降AI模式（中文）": test_rewrite_ai_mode(),
        "降重模式（英文）": test_rewrite_english(),
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

