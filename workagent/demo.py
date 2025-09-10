#!/usr/bin/env python3
"""
多模型智能Agent系统演示脚本
"""
import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from main import AgentSystem
import time

def demo_task_processing():
    """演示任务处理功能"""
    print("🚀 多模型智能Agent系统演示")
    print("="*50)

    # 初始化系统
    print("📦 初始化系统组件...")
    agent = AgentSystem()

    # 演示任务处理
    print("\n🎯 演示任务处理功能:")
    test_tasks = [
        "写一个Python函数计算斐波那契数列",
        "分析数据处理的最佳实践",
        "设计一个简单的REST API"
    ]

    for i, task in enumerate(test_tasks, 1):
        print(f"\n📋 任务 {i}: {task}")
        try:
            result = agent.process_task(task)
            print(f"✅ 结果: {result[:100]}..." if len(str(result)) > 100 else f"✅ 结果: {result}")
        except Exception as e:
            print(f"❌ 处理失败: {e}")
        time.sleep(1)  # 避免请求过于频繁

    # 演示模型对话
    print("\n🤝 演示模型对话功能:")
    try:
        dialogue_result = agent.model_dialogue("系统优化策略")
        print(f"✅ 对话完成，生成了 {len(dialogue_result)} 个新需求")
    except Exception as e:
        print(f"❌ 对话失败: {e}")

    # 演示自我优化
    print("\n🔧 演示自我优化功能:")
    try:
        agent.self_optimize()
        print("✅ 自我优化完成")
    except Exception as e:
        print(f"❌ 优化失败: {e}")

    # 演示新功能
    print("\n📊 演示任务历史管理:")
    try:
        agent.show_task_history()
    except Exception as e:
        print(f"❌ 历史查看失败: {e}")

    print("\n📈 演示性能监控:")
    try:
        agent.show_performance_report()
    except Exception as e:
        print(f"❌ 性能报告失败: {e}")

    print("\n⚙️ 演示配置管理:")
    try:
        agent.show_config()
    except Exception as e:
        print(f"❌ 配置查看失败: {e}")

    print("\n🔌 演示插件系统:")
    try:
        agent.show_plugins()
    except Exception as e:
        print(f"❌ 插件查看失败: {e}")

    print("\n📊 演示数据可视化:")
    try:
        agent.generate_visualization()
    except Exception as e:
        print(f"❌ 可视化失败: {e}")

    print("\n🎉 演示完成！")
    print("系统已实现以下核心功能:")
    print("✅ 多模型协作 (Qwen3, Gemma3, Qwen2.5-coder, DeepSeek-R1)")
    print("✅ 智能任务处理和MCP匹配")
    print("✅ 递归MCP优化算法")
    print("✅ 工作工程自我优化")
    print("✅ 模型互问互答机制")
    print("✅ 实时系统状态监控")
    print("✅ 任务历史管理")
    print("✅ 性能监控和告警")
    print("✅ 配置管理系统")
    print("✅ 插件架构支持")
    print("✅ 数据可视化报告")
    print("✅ 命令行界面交互")

if __name__ == "__main__":
    demo_task_processing()
