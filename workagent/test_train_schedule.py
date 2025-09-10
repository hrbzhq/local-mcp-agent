#!/usr/bin/env python3
"""
高铁查询功能测试脚本
测试修复后的高铁查询功能
"""

import requests
import json

def test_train_schedule():
    """测试高铁查询功能"""
    base_url = "http://localhost:5000"

    test_cases = [
        {
            "task": "查询高铁902次列车的运行表",
            "expected_type": "train_schedule",
            "description": "高铁时刻表查询测试"
        },
        {
            "task": "查询火车G123次的时刻表",
            "expected_type": "train_schedule",
            "description": "火车时刻表查询测试"
        },
        {
            "task": "查询数据库中的所有表",
            "expected_type": "database",
            "description": "数据库查询测试（确保不冲突）"
        },
        {
            "task": "请帮我分析这个网页：https://httpbin.org/html",
            "expected_type": "web_scraping",
            "description": "网页抓取测试"
        }
    ]

    print("🚄 高铁查询功能测试")
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
                print(f"   - 需要外部数据: {analysis.get('requires_external_data', False)}")

                # 显示响应结果
                response_data = result.get("response", {})
                if isinstance(response_data, str):
                    # 如果是字符串响应，显示前200个字符
                    preview = response_data[:200].replace('\n', ' ')
                    print(f"✅ 响应预览: {preview}...")
                elif isinstance(response_data, dict):
                    if "status" in response_data and response_data["status"] == "success":
                        print("✅ 插件执行成功")
                        if "row_count" in response_data:
                            print(f"   - 返回 {response_data['row_count']} 条记录")
                        elif "train_number" in response_data:
                            print(f"   - 车次: {response_data['train_number']}")
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
    print("🎉 高铁查询功能测试完成！")

if __name__ == "__main__":
    test_train_schedule()
