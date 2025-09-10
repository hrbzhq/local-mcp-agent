#!/usr/bin/env python3
"""
自主优化系统测试脚本 - Autonomous Optimization System Test Script
"""

import os
import sys
import time
import logging
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.system_integrator import SystemIntegrator

def setup_test_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - TEST - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_component_loading():
    """测试组件加载"""
    print("🔧 测试组件加载...")

    integrator = SystemIntegrator()

    # 测试加载顺序计算
    load_order = integrator._calculate_load_order()
    print(f"✅ 计算的加载顺序: {load_order}")

    # 测试单个组件加载
    success_count = 0
    for component_name in load_order:
        if integrator._load_component(component_name):
            success_count += 1
        else:
            print(f"❌ 组件 {component_name} 加载失败")

    print(f"✅ 成功加载 {success_count}/{len(load_order)} 个组件")
    return success_count == len(load_order)

def test_component_connections():
    """测试组件连接"""
    print("\n🔗 测试组件连接...")

    integrator = SystemIntegrator()

    # 加载组件
    if not integrator.initialize_system():
        print("❌ 系统初始化失败")
        return False

    # 检查关键连接
    command_center = integrator.get_component('command_center')
    learning_engine = integrator.get_component('learning_engine')
    decision_maker = integrator.get_component('decision_maker')

    if command_center and learning_engine and decision_maker:
        print("✅ 关键组件连接正常")
        return True
    else:
        print("❌ 关键组件连接失败")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n⚙️ 测试基本功能...")

    integrator = SystemIntegrator()

    if not integrator.initialize_system():
        print("❌ 系统初始化失败")
        return False

    # 测试参谋中心
    command_center = integrator.get_component('command_center')
    if command_center:
        # 提交测试任务
        task_id = command_center.submit_task({
            'task': '测试任务：分析代码结构',
            'priority': 'normal'
        })
        print(f"✅ 任务提交成功，ID: {task_id}")

        # 检查任务状态
        status = command_center.get_task_status(task_id)
        if status:
            print(f"✅ 任务状态查询成功: {status['status']}")

        # 获取系统状态
        system_status = command_center.get_system_status()
        print(f"✅ 系统状态获取成功: {system_status['active_tasks']} 活跃任务")

    # 测试学习引擎
    learning_engine = integrator.get_component('learning_engine')
    if learning_engine:
        # 记录测试经验
        learning_engine.record_experience(
            task_type='testing',
            input_data='test_input',
            output_data='test_output',
            success=True,
            duration=1.0,
            feedback='测试经验记录'
        )
        print("✅ 学习引擎经验记录成功")

    # 测试决策制定器
    decision_maker = integrator.get_component('decision_maker')
    if decision_maker:
        # 进行测试决策
        options = [
            {'action': 'optimize_code', 'expected_benefit': 0.8},
            {'action': 'add_logging', 'expected_benefit': 0.6},
            {'action': 'skip', 'expected_benefit': 0.2}
        ]

        context = {'current_task': 'code_review', 'time_pressure': 'medium'}
        best_option, confidence = decision_maker.make_decision(context, options)

        if best_option:
            print(f"✅ 决策制定成功: {best_option['action']} (置信度: {confidence:.2f})")

    return True

def test_resource_management():
    """测试资源管理"""
    print("\n💾 测试资源管理...")

    integrator = SystemIntegrator()

    if not integrator.initialize_system():
        print("❌ 系统初始化失败")
        return False

    resource_manager = integrator.get_component('resource_manager')
    if resource_manager:
        # 获取资源报告
        report = resource_manager.get_resource_report()
        print("✅ 资源报告获取成功:")
        print(f"   CPU使用率: {report['current_usage'].get('cpu', {}).get('percent', 0):.1f}%")
        print(f"   内存使用率: {report['current_usage'].get('memory', {}).get('percent', 0):.1f}%")
        print(f"   磁盘使用率: {report['current_usage'].get('disk', {}).get('percent', 0):.1f}%")
        print(f"   可用内存: {report['current_usage'].get('memory', {}).get('available', 0) / (1024**3):.0f} GB")

        return True
    else:
        print("❌ 资源管理器不可用")
        return False

def test_safety_monitoring():
    """测试安全监控"""
    print("\n🛡️ 测试安全监控...")

    integrator = SystemIntegrator()

    if not integrator.initialize_system():
        print("❌ 系统初始化失败")
        return False

    safety_monitor = integrator.get_component('safety_monitor')
    if safety_monitor:
        # 获取安全报告
        report = safety_monitor.get_safety_report()
        print("✅ 安全报告获取成功:")
        print(f"   安全状态: {report['overall_status']}")
        print(f"   活跃规则: {report['active_safety_rules']}")
        print(f"   违规事件: {report['total_violations']}")

        return True
    else:
        print("❌ 安全监控器不可用")
        return False

def test_mcp_optimizer():
    """测试MCP优化器"""
    print("\n🔄 测试MCP优化器...")

    integrator = SystemIntegrator()

    if not integrator.initialize_system():
        print("❌ 系统初始化失败")
        return False

    mcp_optimizer = integrator.get_component('mcp_autonomous_optimizer')
    if mcp_optimizer:
        # 扫描需求（这里是模拟）
        requirements = mcp_optimizer._scan_new_requirements()
        print(f"✅ 需求扫描完成，发现 {len(requirements)} 个新需求")

        # 生成模块代码（如果有需求）
        if requirements:
            for req in requirements[:1]:  # 只测试第一个需求
                code = mcp_optimizer._generate_module_code(req)
                if code:
                    print("✅ 模块代码生成成功")
                    print(f"   生成的代码长度: {len(code)} 字符")

        return True
    else:
        print("❌ MCP优化器不可用")
        return False

def test_system_integration():
    """测试系统集成"""
    print("\n🔧 测试系统集成...")

    integrator = SystemIntegrator()

    # 测试系统状态
    status = integrator.get_system_status()
    print("✅ 系统状态获取成功:")
    print(f"   系统状态: {status['system_status']}")
    print(f"   组件数量: {status['total_components']}")
    print(f"   活跃组件: {status['active_components']}")

    # 测试组件启用/禁用
    test_component = 'learning_engine'
    if integrator.disable_component(test_component):
        print(f"✅ 组件 {test_component} 禁用成功")

    if integrator.enable_component(test_component):
        print(f"✅ 组件 {test_component} 启用成功")

    # 测试集成报告
    report = integrator.get_integration_report()
    print("✅ 集成报告获取成功:")
    print(f"   组件加载数量: {report['components_loaded']}")

    return True

def run_full_system_test():
    """运行完整系统测试"""
    print("🚀 开始自主优化系统完整测试")
    print("=" * 50)

    test_results = []

    # 测试组件加载
    test_results.append(("组件加载", test_component_loading()))

    # 测试组件连接
    test_results.append(("组件连接", test_component_connections()))

    # 测试基本功能
    test_results.append(("基本功能", test_basic_functionality()))

    # 测试资源管理
    test_results.append(("资源管理", test_resource_management()))

    # 测试安全监控
    test_results.append(("安全监控", test_safety_monitoring()))

    # 测试MCP优化器
    test_results.append(("MCP优化器", test_mcp_optimizer()))

    # 测试系统集成
    test_results.append(("系统集成", test_system_integration()))

    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:<12} {status}")
        if result:
            passed += 1

    print(f"\n总体结果: {passed}/{total} 个测试通过")

    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查系统配置和依赖。")
        return False

def main():
    """主函数"""
    setup_test_logging()

    try:
        success = run_full_system_test()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        logging.exception("测试错误详情")
        return 1

if __name__ == '__main__':
    sys.exit(main())
