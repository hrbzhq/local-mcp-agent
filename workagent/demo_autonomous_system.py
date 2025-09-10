#!/usr/bin/env python3
"""
自主优化系统演示脚本 - Autonomous Optimization System Demo
"""

import os
import sys
import time
import logging
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def setup_demo_logging():
    """设置演示日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - DEMO - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_demo_header():
    """打印演示标题"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    自主优化系统演示                            ║
    ║                 Autonomous Optimization System Demo            ║
    ║                                                              ║
    ║  演示内容:                                                     ║
    ║  • 组件初始化和连接                                           ║
    ║  • 任务提交和处理                                             ║
    ║  • 学习和决策过程                                             ║
    ║  • 资源监控和优化                                             ║
    ║  • 安全监控                                                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def demo_component_initialization():
    """演示组件初始化"""
    print("\n🔧 演示1: 组件初始化")
    print("-" * 50)

    try:
        from src.system_integrator import SystemIntegrator

        integrator = SystemIntegrator()

        # 禁用可能导致数据库锁定的组件
        integrator.disable_component('mcp_autonomous_optimizer')

        print("正在初始化系统组件...")
        if integrator.initialize_system():
            print("✅ 系统初始化成功！")

            status = integrator.get_system_status()
            print(f"📊 系统状态: {status['system_status']}")
            print(f"📦 已加载组件: {status['total_components']} 个")
            print(f"⚡ 活跃组件: {status['active_components']} 个")

            # 显示各组件状态
            print("\n组件状态详情:")
            for name, info in status['components'].items():
                status_icon = "✅" if info['status'] == 'running' else "⏳"
                print(f"  {status_icon} {name}: {info['status']}")

            return integrator
        else:
            print("❌ 系统初始化失败")
            return None

    except Exception as e:
        print(f"❌ 初始化过程中出错: {e}")
        return None

def demo_task_processing(integrator):
    """演示任务处理"""
    print("\n🎯 演示2: 任务处理")
    print("-" * 50)

    try:
        command_center = integrator.get_component('command_center')
        if not command_center:
            print("❌ 参谋中心不可用")
            return

        # 提交几个测试任务
        tasks = [
            "分析项目代码结构",
            "优化系统性能",
            "生成API文档",
            "检查代码质量"
        ]

        task_ids = []
        for task in tasks:
            task_id = command_center.submit_task({'task': task})
            task_ids.append(task_id)
            print(f"✅ 任务已提交: {task_id} - {task}")

        # 等待一会儿让任务被处理
        print("\n⏳ 等待任务处理...")
        time.sleep(2)

        # 检查任务状态
        print("\n📋 任务状态:")
        for task_id in task_ids:
            status = command_center.get_task_status(task_id)
            if status:
                print(f"  • {task_id}: {status['status']}")
            else:
                print(f"  • {task_id}: 未找到")

        # 获取系统状态
        system_status = command_center.get_system_status()
        print("\n📊 系统负载:")
        print(f"  • 活跃任务: {system_status['active_tasks']}")
        print(f"  • 系统负载: {system_status['system_load']:.2f}")

    except Exception as e:
        print(f"❌ 任务处理演示出错: {e}")

def demo_learning_and_decision(integrator):
    """演示学习和决策"""
    print("\n🧠 演示3: 学习和决策")
    print("-" * 50)

    try:
        learning_engine = integrator.get_component('learning_engine')
        decision_maker = integrator.get_component('decision_maker')

        if not learning_engine or not decision_maker:
            print("❌ 学习引擎或决策制定器不可用")
            return

        # 记录一些学习经验
        experiences = [
            {
                'task_type': 'coding',
                'input_data': '优化算法',
                'output_data': '算法优化完成',
                'success': True,
                'duration': 2.5,
                'feedback': '性能提升20%'
            },
            {
                'task_type': 'analysis',
                'input_data': '代码审查',
                'output_data': '发现5个问题',
                'success': True,
                'duration': 1.8,
                'feedback': '代码质量良好'
            }
        ]

        print("记录学习经验...")
        for exp in experiences:
            learning_engine.record_experience(**exp)
            print(f"✅ 经验记录: {exp['task_type']} - {exp['feedback']}")

        # 进行决策演示
        print("\n🧐 进行决策分析...")
        options = [
            {'action': '代码重构', 'expected_benefit': 0.8, 'risk': 0.2},
            {'action': '添加测试', 'expected_benefit': 0.6, 'risk': 0.1},
            {'action': '性能优化', 'expected_benefit': 0.7, 'risk': 0.3}
        ]

        context = {
            'current_task': '系统维护',
            'time_pressure': 'medium',
            'resource_available': 'high'
        }

        best_option, confidence = decision_maker.make_decision(context, options)

        if best_option:
            print("🎯 决策结果:")
            print(f"  • 推荐行动: {best_option['action']}")
            print(f"  • 预期收益: {best_option['expected_benefit']}")
            print(f"  • 置信度: {confidence:.2f}")
        else:
            print("❌ 无法做出决策")

    except Exception as e:
        print(f"❌ 学习决策演示出错: {e}")

def demo_resource_monitoring(integrator):
    """演示资源监控"""
    print("\n💾 演示4: 资源监控")
    print("-" * 50)

    try:
        resource_manager = integrator.get_component('resource_manager')
        if not resource_manager:
            print("❌ 资源管理器不可用")
            return

        # 获取资源报告
        report = resource_manager.get_resource_report()

        print("📊 当前资源使用情况:")
        current = report['current_usage']
        print(f"   CPU使用率: {current.get('cpu', {}).get('percent', 0):.1f}%")
        print(f"   内存使用率: {current.get('memory', {}).get('percent', 0):.1f}%")
        print(f"   磁盘使用率: {current.get('disk', {}).get('percent', 0):.1f}%")
        # 显示建议
        if report['recommendations']:
            print("\n💡 优化建议:")
            for rec in report['recommendations'][:3]:  # 只显示前3个建议
                print(f"  • {rec}")

        # 显示警报
        if report['alerts']:
            print("\n🚨 资源警报:")
            for alert in report['alerts'][:2]:  # 只显示前2个警报
                print(f"  • {alert.get('message', '未知警报')}")

    except Exception as e:
        print(f"❌ 资源监控演示出错: {e}")

def demo_safety_monitoring(integrator):
    """演示安全监控"""
    print("\n🛡️ 演示5: 安全监控")
    print("-" * 50)

    try:
        safety_monitor = integrator.get_component('safety_monitor')
        if not safety_monitor:
            print("❌ 安全监控器不可用")
            return

        # 获取安全报告
        report = safety_monitor.get_safety_report()

        print("🔒 安全状态:")
        print(f"  • 整体状态: {report['overall_status']}")
        print(f"  • 活跃规则: {report['active_safety_rules']} 个")
        print(f"  • 违规事件: {report['total_violations']} 个")

        if report['violation_types']:
            print("\n⚠️ 违规类型统计:")
            for violation_type, count in list(report['violation_types'].items())[:3]:
                print(f"  • {violation_type}: {count} 次")

        if report['recent_events']:
            print("\n📝 最近安全事件:")
            for event in report['recent_events'][:2]:
                print(f"  • {event['timestamp'][:19]} - {event['description']}")

    except Exception as e:
        print(f"❌ 安全监控演示出错: {e}")

def demo_performance_report(integrator):
    """演示性能报告"""
    print("\n📈 演示6: 性能报告")
    print("-" * 50)

    try:
        command_center = integrator.get_component('command_center')
        if not command_center:
            print("❌ 参谋中心不可用")
            return

        # 获取性能报告
        report = command_center.get_performance_report()

        print("📊 性能报告:")
        print(f"  • 生成时间: {report['generated_at'][:19]}")
        print(".2%")
        print(".2f")
        print(f"  • 处理任务总数: {report['overall_metrics'].get('total_tasks_processed', 0)}")

        if report['model_performance']:
            print("\n🤖 模型性能:")
            for model_name, perf in list(report['model_performance'].items())[:3]:
                print(".2%")
                print(".2f")
                print(f"      使用次数: {perf['usage_count']}")

        if report['recommendations']:
            print("\n💡 性能建议:")
            for rec in report['recommendations'][:2]:
                print(f"  • {rec}")

    except Exception as e:
        print(f"❌ 性能报告演示出错: {e}")

def run_demo():
    """运行完整演示"""
    setup_demo_logging()
    print_demo_header()

    # 演示1: 组件初始化
    integrator = demo_component_initialization()
    if not integrator:
        print("❌ 演示无法继续，系统初始化失败")
        return False

    # 演示2: 任务处理
    demo_task_processing(integrator)

    # 演示3: 学习和决策
    demo_learning_and_decision(integrator)

    # 演示4: 资源监控
    demo_resource_monitoring(integrator)

    # 演示5: 安全监控
    demo_safety_monitoring(integrator)

    # 演示6: 性能报告
    demo_performance_report(integrator)

    # 演示结束
    print("\n" + "=" * 60)
    print("🎉 自主优化系统演示完成！")
    print("=" * 60)
    print("\n主要特性展示:")
    print("✅ 模块化架构 - 系统由多个独立组件组成")
    print("✅ 自主学习 - 系统能从经验中学习和改进")
    print("✅ 智能决策 - 基于数据做出最优决策")
    print("✅ 资源优化 - 自动监控和优化系统资源")
    print("✅ 安全保障 - 多层次的安全监控和保护")
    print("✅ 任务协调 - 智能分配和处理多任务")
    print("\n🚀 系统已准备就绪，可以处理实际任务！")

    # 清理资源
    try:
        integrator.shutdown_system()
        print("\n🧹 系统已安全关闭")
    except Exception as e:
        print(f"\n⚠️ 系统关闭时出现问题: {e}")

    return True

def main():
    """主函数"""
    try:
        success = run_demo()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        logging.exception("演示错误详情")
        return 1

if __name__ == '__main__':
    sys.exit(main())
