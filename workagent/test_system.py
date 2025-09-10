#!/usr/bin/env python3
"""
智能Agent系统测试脚本
测试系统的智能分析和MCP查询功能
"""

import requests
import json
import time

def test_system():
    """测试系统功能"""
    base_url = "http://localhost:5000"

    test_cases = [
        {
            "task": "查询数据库中的所有表",
            "expected_type": "database",
            "description": "数据库查询测试"
        },
        {
            "task": "请帮我分析这个网页：https://httpbin.org/html",
            "expected_type": "web_scraping",
            "description": "网页抓取测试"
        },
        {
            "task": "系统状态如何？",
            "expected_type": "general",
            "description": "一般查询测试"
        }
    ]

    print("🚀 开始测试智能Agent系统...")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}: {test_case['description']}")
        print(f"任务: {test_case['task']}")

        try:
            # 发送请求
            response = requests.post(
                f"{base_url}/api/tasks",
                json={"task": test_case["task"], "model": "qwen3"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # 显示分析结果
                analysis = result.get("analysis", {})
                print(f"🔍 任务分析:")
                print(f"   - 类型: {analysis.get('task_type', 'unknown')}")
                print(f"   - 意图: {analysis.get('intent', 'unknown')}")
                print(f"   - 复杂度: {analysis.get('complexity', 'unknown')}")
                print(f"   - 需要外部数据: {analysis.get('requires_external_data', False)}")

                # 显示响应结果
                response_data = result.get("response", {})
                if isinstance(response_data, dict):
                    if "status" in response_data and response_data["status"] == "success":
                        print("✅ 插件执行成功")
                        if "row_count" in response_data:
                            print(f"   - 返回 {response_data['row_count']} 条记录")
                        elif "status_code" in response_data:
                            print(f"   - HTTP状态码: {response_data['status_code']}")
                    else:
                        print("🤖 模型响应")
                        print(f"   - 响应长度: {len(str(response_data))} 字符")
                else:
                    print("🤖 模型响应")
                    print(f"   - 响应长度: {len(str(response_data))} 字符")

                print("✅ 测试通过")

            else:
                print(f"❌ HTTP错误: {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

        time.sleep(1)  # 短暂延迟

    print("\n" + "=" * 50)
    print("🎉 测试完成！")

if __name__ == "__main__":
    test_system()
