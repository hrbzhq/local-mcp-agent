#!/usr/bin/env python3
"""
模型连接测试脚本
"""
import requests


def test_ollama_models():
    """测试Ollama模型连接"""
    base_url = "http://127.0.0.1:11434"

    # 获取可用模型
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = response.json()['models']
            print("📋 发现 {} 个模型:".format(len(models)))
            for model in models:
                print(f"   - {model['name']} ({model['details']['parameter_size']})")
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 连接Ollama失败: {e}")
        return

    # 测试每个模型
    test_models = ['qwen3:0.6b', 'gemma3:270m', 'qwen2.5-coder:0.5b', 'deepseek-r1:1.5b']

    print("\n🔧 测试模型调用:")
    for model_name in test_models:
        try:
            print("\n测试 {}:".format(model_name))
            payload = {
                "model": model_name,
                "prompt": "Say 'Hello' in one word",
                "stream": False
            }
            response = requests.post(f"{base_url}/api/generate", json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                print("   ✅ 成功: {}".format(result.get('response', 'No response')))
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            print("   ⏰ 超时")
        except Exception as e:
            print(f"   ❌ 错误: {e}")


def test_agent_system():
    """测试完整的Agent系统"""
    print("\n🤖 测试多模型智能Agent系统:")

    try:
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        sys.path.insert(0, src_dir)

        from main import AgentSystem

        # 初始化系统
        print("📦 初始化Agent系统...")
        agent = AgentSystem()

        # 测试基本功能
        print("🔧 测试基本功能...")

        # 测试任务处理
        test_task = "写一个简单的Hello World程序"
        print(f"📋 测试任务: {test_task}")
        result = agent.process_task(test_task)
        print(f"✅ 任务结果: {result[:100]}..." if len(str(result)) > 100 else f"✅ 任务结果: {result}")

        # 测试模型管理器
        print("\n🔧 测试模型管理器...")
        test_results = agent.model_manager.test_models()
        for model, status in test_results.items():
            print(f"   {model}: {status}")

        # 测试MCP管理器
        print("\n🔧 测试MCP管理器...")
        mcp_content = agent.mcp_manager.get_mcp("test_module")
        if mcp_content:
            print("   ✅ MCP检索成功")
        else:
            print("   ⚠️  MCP检索返回空结果")

        # 测试任务历史管理器
        print("\n🔧 测试任务历史管理器...")
        history = agent.task_history.get_recent_tasks(5)
        print(f"   📊 最近任务数: {len(history) if history else 0}")

        # 测试性能监控器
        print("\n🔧 测试性能监控器...")
        report = agent.performance_monitor.get_performance_report()
        if 'error' in report:
            print(f"   ⚠️ 性能报告: {report['error']}")
        else:
            print(f"   📈 CPU使用率: {report['averages']['cpu_percent']:.1f}%")

        # 测试配置管理器
        print("\n🔧 测试配置管理器...")
        config = agent.config_manager.get_config_summary()
        print(f"   ⚙️ 配置项数: {len(config)}")

        # 测试插件管理器
        print("\n🔧 测试插件管理器...")
        plugins = agent.plugin_manager.list_plugins()
        print(f"   🔌 已加载插件数: {len(plugins)}")

        # 测试数据可视化器
        print("\n🔧 测试数据可视化器...")
        try:
            # 获取性能数据
            perf_data = agent.performance_monitor.get_metrics_history(60)
            if perf_data:
                agent.data_visualizer.create_performance_dashboard(perf_data)
                print("   📊 可视化报告生成成功")
            else:
                print("   ⚠️ 没有足够的性能数据生成可视化报告")
        except Exception as e:
            print(f"   ❌ 可视化报告生成失败: {e}")

        print("\n🎉 系统测试完成！")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 系统测试失败: {e}")


if __name__ == "__main__":
    test_ollama_models()
    test_agent_system()
