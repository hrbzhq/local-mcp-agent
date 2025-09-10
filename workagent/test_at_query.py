#!/usr/bin/env python3
"""
@查询功能测试脚本
测试@查询语法和MCP服务支持
"""

import requests
import json

def test_at_query():
    """测试@查询功能"""
    base_url = "http://localhost:5000"

    test_cases = [
        {
            "task": "@help",
            "description": "@查询帮助信息"
        },
        {
            "task": "@web python教程",
            "description": "@web网页查询测试"
        },
        {
            "task": "@code 机器学习算法",
            "description": "@code编程查询测试"
        },
        {
            "task": "@api RESTful设计",
            "description": "@api接口查询测试"
        },
        {
            "task": "@data 数据可视化",
            "description": "@data数据查询测试"
        },
        {
            "task": "@train G902",
            "description": "@train列车查询测试"
        },
        {
            "task": "@人工智能发展趋势",
            "description": "通用@查询测试"
        },
        {
            "task": "查询数据库中的所有表",
            "description": "普通数据库查询测试（确保不冲突）"
        }
    ]

    print("🎯 @查询功能测试")
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
                print(f"   - @查询: {analysis.get('is_at_query', False)}")
                print(f"   - 需要外部数据: {analysis.get('requires_external_data', False)}")

                # 显示响应结果
                response_data = result.get("response", {})
                if isinstance(response_data, str):
                    # 如果是字符串响应，显示前300个字符
                    preview = response_data[:300].replace('\n', ' ')
                    print(f"✅ 响应预览: {preview}...")
                elif isinstance(response_data, dict):
                    if "status" in response_data and response_data["status"] == "success":
                        print("✅ 插件执行成功")
                        if "row_count" in response_data:
                            print(f"   - 返回 {response_data['row_count']} 条记录")
                    else:
                        print("🤖 模型响应")
                        preview = str(response_data)[:200]
                        print(f"   - 响应预览: {preview}...")
                else:
                    print("🤖 模型响应")
                    preview = str(response_data)[:200]
                    print(f"   - 响应预览: {preview}...")

                print("✅ 测试通过")

            else:
                print(f"❌ HTTP错误: {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 50)
    print("🎉 @查询功能测试完成！")

if __name__ == "__main__":
    test_at_query()
