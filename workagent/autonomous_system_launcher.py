#!/usr/bin/env python3
"""
自主优化系统启动器 - Autonomous Optimization System Launcher
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.system_integrator import SystemIntegrator

def setup_logging():
    """设置日志"""
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'autonomous_system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    自主优化系统启动器                          ║
    ║                 Autonomous Optimization System                 ║
    ║                                                              ║
    ║  组件列表:                                                     ║
    ║  • 自主优化核心 (Self-Optimization Core)                      ║
    ║  • 学习引擎 (Learning Engine)                                ║
    ║  • 决策制定器 (Decision Maker)                               ║
    ║  • 资源管理器 (Resource Manager)                             ║
    ║  • 安全监控器 (Safety Monitor)                               ║
    ║  • MCP自主优化器 (MCP Autonomous Optimizer)                  ║
    ║  • 参谋中心 (Command Center)                                 ║
    ║                                                              ║
    ║  系统正在初始化中...                                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_status(system_status):
    """打印系统状态"""
    print("\n" + '='*60)
    print("系统状态报告")
    print('='*60)

    print(f"系统整体状态: {system_status['system_status']}")
    print(f"组件总数: {system_status['total_components']}")
    print(f"活跃组件: {system_status['active_components']}")
    print(f"时间戳: {system_status['timestamp']}")

    print("\n组件状态:")
    for name, status in system_status['components'].items():
        status_icon = "✅" if status['status'] == 'running' else "❌" if status['status'] == 'error' else "⏳"
        print(f"  {status_icon} {name}: {status['status']}")
        print(f"    最后健康检查: {status['last_health_check']}")
        if status['restart_count'] > 0:
            print(f"    重启次数: {status['restart_count']}")

def interactive_mode(integrator):
    """交互模式"""
    print("\n进入交互模式。输入 'help' 查看可用命令。")

    commands = {
        'help': '显示帮助信息',
        'status': '显示系统状态',
        'components': '列出所有组件',
        'enable <component>': '启用指定组件',
        'disable <component>': '禁用指定组件',
        'restart <component>': '重启指定组件',
        'task <description>': '提交任务到参谋中心',
        'performance': '显示性能报告',
        'shutdown': '关闭系统并退出',
        'exit': '退出交互模式'
    }

    while True:
        try:
            command = input("\n自主优化系统 > ").strip().lower()

            if command == 'help':
                print("\n可用命令:")
                for cmd, desc in commands.items():
                    print(f"  {cmd:<20} - {desc}")

            elif command == 'status':
                status = integrator.get_system_status()
                print_status(status)

            elif command == 'components':
                status = integrator.get_system_status()
                print("\n已加载的组件:")
                for name, info in status['components'].items():
                    print(f"  • {name} ({info['status']})")

            elif command.startswith('enable '):
                component = command[7:].strip()
                if integrator.enable_component(component):
                    print(f"组件 {component} 已启用")
                else:
                    print(f"启用组件 {component} 失败")

            elif command.startswith('disable '):
                component = command[8:].strip()
                if integrator.disable_component(component):
                    print(f"组件 {component} 已禁用")
                else:
                    print(f"禁用组件 {component} 失败")

            elif command.startswith('restart '):
                component = command[8:].strip()
                integrator._restart_component(component)
                print(f"正在重启组件 {component}")

            elif command.startswith('task '):
                task_desc = command[5:].strip()
                command_center = integrator.get_component('command_center')
                if command_center:
                    task_id = command_center.submit_task({'task': task_desc})
                    print(f"任务已提交，ID: {task_id}")
                else:
                    print("参谋中心不可用")

            elif command == 'performance':
                command_center = integrator.get_component('command_center')
                if command_center:
                    report = command_center.get_performance_report()
                    print("\n性能报告:")
                    print(f"生成时间: {report['generated_at']}")
                    print(f"整体成功率: {report['overall_metrics'].get('overall_success_rate', 0):.2%}")
                    print(f"平均响应时间: {report['overall_metrics'].get('overall_avg_response_time', 0):.2f}s")
                    print(f"处理任务总数: {report['overall_metrics'].get('total_tasks_processed', 0)}")
                else:
                    print("参谋中心不可用")

            elif command in ['shutdown', 'exit']:
                print("正在关闭系统...")
                integrator.shutdown_system()
                break

            else:
                print("未知命令。输入 'help' 查看可用命令。")

        except KeyboardInterrupt:
            print("\n收到中断信号，正在关闭系统...")
            integrator.shutdown_system()
            break
        except Exception as e:
            print(f"命令执行出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自主优化系统启动器')
    parser.add_argument('--mode', choices=['auto', 'interactive'], default='interactive',
                       help='运行模式：auto（自动）或 interactive（交互）')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别')

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # 打印横幅
    print_banner()

    # 创建系统集成器
    integrator = SystemIntegrator()

    try:
        # 初始化系统
        logging.info("开始初始化自主优化系统...")
        if not integrator.initialize_system():
            logging.error("系统初始化失败")
            return 1

        # 启动健康监控
        integrator.start_health_monitoring()

        # 显示初始状态
        initial_status = integrator.get_system_status()
        print_status(initial_status)

        if args.mode == 'auto':
            # 自动模式：运行一段时间后退出
            logging.info("进入自动模式，系统将运行60秒...")
            time.sleep(60)
            logging.info("自动模式运行完成")
        else:
            # 交互模式
            interactive_mode(integrator)

    except KeyboardInterrupt:
        logging.info("收到中断信号")
    except Exception as e:
        logging.error(f"系统运行出错: {e}")
        return 1
    finally:
        # 确保系统正确关闭
        if integrator.system_status != 'stopped':
            integrator.shutdown_system()

    logging.info("自主优化系统已关闭")
    return 0

if __name__ == '__main__':
    sys.exit(main())
