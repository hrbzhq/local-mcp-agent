#!/usr/bin/env python3
"""
演示Agent自主优化和MCP进化优化功能
"""

import sys
import os
import time
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.self_optimization_core import SelfOptimizationCore

def demonstrate_capability_expansion():
    """演示能力边界扩展"""
    print("\n" + "="*60)
    print("🎯 Agent自主优化 - 能力边界扩展演示")
    print("="*60)

    core = SelfOptimizationCore()

    print("📊 1. 模拟能力使用情况...")
    # 模拟各种能力的频繁使用
    capabilities = [
        ("text_processing", True, 20),    # 高频使用，成功
        ("data_analysis", False, 15),     # 中频使用，失败率高
        ("api_integration", True, 12),    # 中频使用，成功
        ("image_processing", True, 3),    # 低频使用，成功
        ("code_generation", False, 8),    # 中低频使用，失败
    ]

    for capability, success, count in capabilities:
        for _ in range(count):
            core.capability_expander.record_capability_usage(capability, success)

    print("✅ 已记录能力使用数据")

    print("\n📈 2. 执行能力分析...")
    core.capability_expander._analyze_capability_usage()
    core.capability_expander._identify_skill_gaps()

    status = core.get_capability_expansion_status()
    print(f"📊 分析结果: {status['capability_count']} 个能力，{status['skill_gaps_count']} 个技能空白")

    print("\n🎯 3. 制定扩展计划...")
    expansion_plan = core.capability_expander._create_expansion_plan()
    print(f"📋 扩展计划: {len(expansion_plan)} 个任务")
    for i, task in enumerate(expansion_plan, 1):
        print(f"   {i}. {task['description']} (优先级: {task['priority']})")

    print("\n🚀 4. 执行能力扩展...")
    if expansion_plan:
        core.capability_expander._execute_expansion_plan(expansion_plan)
        print("✅ 能力扩展执行完成")
    else:
        print("ℹ️  暂无需要扩展的能力")

def demonstrate_mcp_evolution():
    """演示MCP进化优化"""
    print("\n" + "="*60)
    print("🔧 MCP自主优化 - 质量与数量的双重进化演示")
    print("="*60)

    core = SelfOptimizationCore()

    print("📊 1. 分析现有MCP模块...")
    core.mcp_evolution_optimizer._analyze_module_usage()

    status = core.get_mcp_evolution_status()
    print(f"📊 发现模块: {status['module_count']} 个")

    print("\n📈 2. 评估模块质量...")
    core.mcp_evolution_optimizer._assess_module_quality()
    status = core.get_mcp_evolution_status()
    print(f"📊 质量评估: {status['quality_assessed']} 个模块，平均质量: {status['avg_quality']:.2f}")
    print("\n🔍 3. 发现新需求...")
    new_requirements = core.mcp_evolution_optimizer._discover_new_requirements()
    print(f"📋 新需求: {len(new_requirements)} 个")
    for i, req in enumerate(new_requirements[:3], 1):  # 只显示前3个
        print(f"   {i}. {req['description']} (优先级: {req['priority']})")

    print("\n🎯 4. 制定进化计划...")
    evolution_plan = core.mcp_evolution_optimizer._create_evolution_plan(new_requirements)
    print(f"📋 进化计划: {len(evolution_plan)} 个任务")
    for i, task in enumerate(evolution_plan, 1):
        print(f"   {i}. {task['description']} (优先级: {task['priority']})")

    print("\n🚀 5. 执行MCP进化...")
    if evolution_plan:
        core.mcp_evolution_optimizer._execute_evolution_plan(evolution_plan)
        print("✅ MCP进化执行完成")
    else:
        print("ℹ️  暂无需要进化的模块")

def demonstrate_integrated_system():
    """演示集成系统"""
    print("\n" + "="*60)
    print("🤖 完整自主优化系统演示")
    print("="*60)

    core = SelfOptimizationCore()

    print("🚀 启动自主优化系统...")
    core.start_autonomous_optimization()

    print("\n⏰ 系统运行计划:")
    print("   • 每5分钟: 执行常规资源和性能优化")
    print("   • 每1小时: 执行能力边界扩展")
    print("   • 每2小时: 执行MCP质量与数量进化")

    print("\n📊 实时状态监控:")
    for i in range(3):
        time.sleep(1)
        cap_status = core.get_capability_expansion_status()
        mcp_status = core.get_mcp_evolution_status()
        print(f"   能力扩展: {cap_status.get('capability_count', 0)} 个能力")
        print(f"   MCP进化: {mcp_status.get('module_count', 0)} 个模块")
        print()

    print("🛑 停止系统...")
    core.stop_autonomous_optimization()
    print("✅ 系统已安全停止")

def show_system_architecture():
    """展示系统架构"""
    print("\n" + "="*60)
    print("🏗️  系统架构概述")
    print("="*60)

    architecture = """
🤖 Agent自主优化系统
├── 🎯 能力边界扩展器 (CapabilityBoundaryExpander)
│   ├── 基于使用频率分析能力需求
│   ├── 主动学习新技能
│   ├── 扩展Agent能力边界
│   └── 智能优先级排序
│
├── 🔧 MCP进化优化器 (MCPEvolutionOptimizer)
│   ├── 质量评估现有模块
│   ├── 发现新需求模式
│   ├── 自动生成新模块
│   └── 持续改进模块质量
│
└── 🎛️ 自主优化核心 (SelfOptimizationCore)
    ├── 协调所有优化组件
    ├── 智能调度优化任务
    ├── 基于频率的资源分配
    └── 确保不影响主要工作

优化策略:
• 高频使用 + 高成功率 → 保持现状
• 高频使用 + 低成功率 → 优先改进
• 新兴需求模式 → 主动学习
• 低频使用项目 → 降低优先级
• 主要工作时间 → 避免干扰
"""

    print(architecture)

if __name__ == "__main__":
    print("🎉 欢迎使用Agent自主优化和MCP进化优化系统演示")

    show_system_architecture()
    demonstrate_capability_expansion()
    demonstrate_mcp_evolution()
    demonstrate_integrated_system()

    print("\n" + "="*60)
    print("🎊 演示完成！")
    print("💡 系统现在可以:")
    print("   • 主动发现和学习新能力")
    print("   • 持续改进MCP模块质量")
    print("   • 智能分配优化资源")
    print("   • 避免干扰主要工作流程")
    print("="*60)
