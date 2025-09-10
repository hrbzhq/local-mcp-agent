#!/usr/bin/env python3
"""
测试Agent自主优化和MCP进化优化功能
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.self_optimization_core import SelfOptimizationCore

def test_capability_expansion():
    """测试能力边界扩展"""
    print("=== 测试能力边界扩展 ===")

    core = SelfOptimizationCore()

    # 模拟一些能力使用记录
    for i in range(5):
        core.capability_expander.record_capability_usage("text_processing", success=True)
        core.capability_expander.record_capability_usage("data_analysis", success=False)
        core.capability_expander.record_capability_usage("api_integration", success=True)

    # 获取扩展状态
    status = core.get_capability_expansion_status()
    print(f"能力扩展状态: {status}")

    # 执行一次扩展
    core._execute_capability_expansion()
    print("能力边界扩展执行完成")

def test_mcp_evolution():
    """测试MCP进化优化"""
    print("\n=== 测试MCP进化优化 ===")

    core = SelfOptimizationCore()

    # 模拟一些模块使用记录
    core.mcp_evolution_optimizer.record_module_usage("database")
    core.mcp_evolution_optimizer.record_module_usage("web_scraper")
    core.mcp_evolution_optimizer.record_module_usage("file_processor")

    # 获取进化状态
    status = core.get_mcp_evolution_status()
    print(f"MCP进化状态: {status}")

    # 执行一次进化
    core._execute_mcp_evolution()
    print("MCP进化优化执行完成")

def test_integrated_optimization():
    """测试集成优化"""
    print("\n=== 测试集成优化系统 ===")

    core = SelfOptimizationCore()

    # 启动优化系统
    core.start_autonomous_optimization()

    print("自主优化系统已启动")
    print("系统将每5分钟执行一次常规优化")
    print("每1小时执行一次能力边界扩展")
    print("每2小时执行一次MCP进化优化")

    # 等待一段时间观察
    time.sleep(2)

    # 获取系统状态
    print("\n系统状态:")
    print(f"能力扩展: {core.get_capability_expansion_status()}")
    print(f"MCP进化: {core.get_mcp_evolution_status()}")

    # 停止系统
    core.stop_autonomous_optimization()
    print("自主优化系统已停止")

if __name__ == "__main__":
    try:
        test_capability_expansion()
        test_mcp_evolution()
        test_integrated_optimization()
        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
