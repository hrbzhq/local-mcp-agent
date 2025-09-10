#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本
测试模型管理、插件中心、历史记录等功能
"""

import requests
import json
import time

class SystemTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_models_api(self):
        """测试模型管理API"""
        print("🔍 测试模型管理API...")

        try:
            # 获取模型列表
            response = self.session.get(f"{self.base_url}/api/models")
            if response.status_code == 200:
                models_data = response.json()
                print(f"✅ 获取模型列表成功: {len(models_data.get('models', []))} 个模型")

                # 测试第一个模型
                if models_data.get('models'):
                    first_model = models_data['models'][0]['id']
                    print(f"🧪 测试模型: {first_model}")

                    # 获取模型信息
                    response = self.session.get(f"{self.base_url}/api/models/{first_model}")
                    if response.status_code == 200:
                        print("✅ 获取模型信息成功")
                    else:
                        print(f"❌ 获取模型信息失败: {response.status_code}")

                    # 测试模型功能
                    response = self.session.post(f"{self.base_url}/api/models/{first_model}/test")
                    if response.status_code == 200:
                        test_result = response.json()
                        if test_result.get('success'):
                            print(f"✅ 模型测试成功 ({test_result.get('execution_time', 0):.2f}s)")
                        else:
                            print(f"❌ 模型测试失败: {test_result.get('response', '未知错误')}")
                    else:
                        print(f"❌ 模型测试请求失败: {response.status_code}")
            else:
                print(f"❌ 获取模型列表失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 模型API测试失败: {e}")

    def test_plugins_api(self):
        """测试插件中心API"""
        print("\n🔌 测试插件中心API...")

        try:
            # 获取插件列表
            response = self.session.get(f"{self.base_url}/api/plugins")
            if response.status_code == 200:
                plugins_data = response.json()
                print(f"✅ 获取插件列表成功: {len(plugins_data.get('plugins', []))} 个插件")

                stats = plugins_data.get('stats', {})
                print(f"📊 插件统计: 总共 {stats.get('total_plugins', 0)} 个，已加载 {stats.get('loaded_plugins', 0)} 个")

                # 测试第一个插件
                if plugins_data.get('plugins'):
                    first_plugin = plugins_data['plugins'][0]['name']
                    print(f"🔧 测试插件: {first_plugin}")

                    # 获取插件信息
                    response = self.session.get(f"{self.base_url}/api/plugins/{first_plugin}")
                    if response.status_code == 200:
                        print("✅ 获取插件信息成功")
                    else:
                        print(f"❌ 获取插件信息失败: {response.status_code}")

                    # 测试插件重新加载
                    response = self.session.post(f"{self.base_url}/api/plugins/{first_plugin}/reload")
                    if response.status_code == 200:
                        reload_result = response.json()
                        if reload_result.get('message'):
                            print("✅ 插件重新加载成功")
                        else:
                            print(f"❌ 插件重新加载失败: {reload_result.get('error', '未知错误')}")
                    else:
                        print(f"❌ 插件重新加载请求失败: {response.status_code}")
            else:
                print(f"❌ 获取插件列表失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 插件API测试失败: {e}")

    def test_history_api(self):
        """测试历史记录API"""
        print("\n📚 测试历史记录API...")

        try:
            # 获取历史记录
            response = self.session.get(f"{self.base_url}/api/history?limit=5")
            if response.status_code == 200:
                history_data = response.json()
                history_count = len(history_data.get('history', []))
                print(f"✅ 获取历史记录成功: {history_count} 条记录")

                # 获取统计信息
                response = self.session.get(f"{self.base_url}/api/history/stats")
                if response.status_code == 200:
                    stats = response.json()
                    print(f"📊 历史统计: 总任务 {stats.get('total_tasks', 0)} 个，成功率 {stats.get('success_rate', 0):.1f}%")
                else:
                    print(f"❌ 获取统计信息失败: {response.status_code}")

                # 测试搜索功能
                if history_count > 0:
                    response = self.session.get(f"{self.base_url}/api/history/search?q=test")
                    if response.status_code == 200:
                        search_data = response.json()
                        print(f"✅ 搜索功能正常: 找到 {len(search_data.get('results', []))} 条匹配记录")
                    else:
                        print(f"❌ 搜索功能失败: {response.status_code}")

                # 测试导出功能
                response = self.session.get(f"{self.base_url}/api/history/export?format=json")
                if response.status_code == 200:
                    print("✅ 导出功能正常")
                else:
                    print(f"❌ 导出功能失败: {response.status_code}")

            else:
                print(f"❌ 获取历史记录失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 历史记录API测试失败: {e}")

    def test_task_execution(self):
        """测试任务执行功能"""
        print("\n⚡ 测试任务执行功能...")

        test_tasks = [
            "请简单介绍一下Python编程语言",
            "@help",
            "@web python教程",
            "计算 2 + 2 等于几？"
        ]

        for i, task in enumerate(test_tasks, 1):
            print(f"  测试任务 {i}: {task}")
            try:
                response = self.session.post(
                    f"{self.base_url}/api/tasks",
                    json={"task": task, "model": "qwen3"},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        print(f"    ✅ 任务执行成功")
                    else:
                        print(f"    ❌ 任务执行失败: {result.get('response', '未知错误')}")
                else:
                    print(f"    ❌ 请求失败: {response.status_code}")

            except Exception as e:
                print(f"    ❌ 任务执行异常: {e}")

            time.sleep(1)  # 避免请求过于频繁

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 系统功能测试")
        print("=" * 60)

        # 检查系统状态
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                print("✅ 系统状态正常")
            else:
                print("❌ 系统未启动或不可访问")
                return
        except Exception as e:
            print(f"❌ 无法连接到系统: {e}")
            return

        print("\n开始测试...\n")

        # 运行各项测试
        self.test_models_api()
        self.test_plugins_api()
        self.test_history_api()
        self.test_task_execution()

        print("\n" + "=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)

def main():
    """主函数"""
    print("系统功能测试工具")
    print("请确保系统已启动 (python start.py --web)")
    print("-" * 40)

    tester = SystemTest()

    print("选择测试模式:")
    print("1. 运行完整测试")
    print("2. 仅测试模型管理")
    print("3. 仅测试插件中心")
    print("4. 仅测试历史记录")
    print("5. 仅测试任务执行")

    choice = input("请选择 (1-5): ").strip()

    if choice == "1":
        tester.run_all_tests()
    elif choice == "2":
        tester.test_models_api()
    elif choice == "3":
        tester.test_plugins_api()
    elif choice == "4":
        tester.test_history_api()
    elif choice == "5":
        tester.test_task_execution()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
