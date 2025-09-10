#!/usr/bin/env python3
"""
性能监控演示脚本
展示系统性能监控功能，包括实时监控、告警系统和性能报告
"""

import time
import logging
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.performance_monitor import PerformanceMonitor

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/performance_demo.log'),
            logging.StreamHandler()
        ]
    )

def demonstrate_basic_monitoring():
    """演示基本性能监控功能"""
    print("\n" + "="*60)
    print("🚀 性能监控演示 - 基本功能")
    print("="*60)
    print("💡 注意: 新的性能监控系统采用按需启动模式")
    print("   - 默认不自动启动监控，节省系统资源")
    print("   - 只有用户主动启动时才开始收集数据")
    print("   - 支持智能停止机制")

    monitor = PerformanceMonitor(history_size=100)

    print("📊 手动启动性能监控...")
    monitor.start_monitoring(interval=1.0)

    print("⏳ 监控中... (10秒)")
    for i in range(10):
        time.sleep(1)
        metrics = monitor.get_current_metrics()
        if 'cpu' in metrics:
            print(f"   CPU: {metrics.get('cpu', {}).get('percent', 0):.1f}% "
                  f"内存: {metrics.get('memory', {}).get('percent', 0):.1f}% "
                  f"磁盘: {metrics.get('disk', {}).get('percent', 0):.1f}%")

    print("🛑 手动停止监控...")
    monitor.stop_monitoring()

    return monitor

def demonstrate_alerts():
    """演示告警功能"""
    print("\n" + "="*60)
    print("🚨 性能监控演示 - 告警功能")
    print("="*60)

    monitor = PerformanceMonitor()

    # 设置较低的阈值来触发告警
    monitor.set_threshold('cpu_percent', 5.0)  # 5% CPU阈值
    monitor.set_threshold('memory_percent', 10.0)  # 10% 内存阈值

    def alert_callback(alert):
        print(f"🚨 告警触发: {alert['message']}")
        print(f"   类型: {alert['type']}")
        print(f"   值: {alert['value']:.1f}, 阈值: {alert['threshold']}")

    monitor.add_alert_callback(alert_callback)

    print("📊 启动监控 (设置低阈值以触发告警)...")
    monitor.start_monitoring(interval=0.5)

    print("⏳ 监控中... (15秒)")
    for i in range(30):
        time.sleep(0.5)
        if i % 10 == 0:
            metrics = monitor.get_current_metrics()
            print(f"   第{i//2 + 1}秒 - CPU: {metrics.get('cpu', {}).get('percent', 0):.1f}%")

    monitor.stop_monitoring()

    print(f"📋 告警历史: {len(monitor.alerts)} 个告警")
    for alert in monitor.alerts[-3:]:  # 显示最后3个告警
        print(f"   {alert['timestamp'].strftime('%H:%M:%S')}: {alert['message']}")

    return monitor

def demonstrate_reporting():
    """演示性能报告功能"""
    print("\n" + "="*60)
    print("📈 性能监控演示 - 报告功能")
    print("="*60)

    monitor = PerformanceMonitor()

    print("📊 收集性能数据...")
    monitor.start_monitoring(interval=0.5)

    print("⏳ 数据收集中... (30秒)")
    for i in range(60):
        time.sleep(0.5)
        if i % 20 == 0:
            print("   已收集 {} 秒数据...".format(i//2))

    monitor.stop_monitoring()

    print("📋 生成性能报告...")

    # 生成不同时间段的报告
    for minutes in [1, 5, 10]:
        print("\n--- 最近 {} 分钟报告 ---".format(minutes))
        report = monitor.get_performance_report(minutes)

        if 'error' in report:
            print(f"❌ 报告错误: {report['error']}")
            continue

    print("📊 数据点: {}".format(report['data_points']))
    print("📈 平均值:")
    print("   CPU: {0:.1f}%".format(report['averages']['cpu_percent']))
    print("   内存: {0:.1f}%".format(report['averages']['memory_percent']))
    print("   磁盘: {0:.1f}%".format(report['averages']['disk_percent']))
    print("📉 峰值:")
    print("   CPU: {0:.1f}%".format(report['peaks']['cpu_percent']))
    print("   内存: {0:.1f}%".format(report['peaks']['memory_percent']))
    print("   磁盘: {0:.1f}%".format(report['peaks']['disk_percent']))
    print("📊 趋势: {}".format(report.get('trend')))
    print("🚨 告警数量: {}".format(report.get('alerts_count')))

    return monitor

def demonstrate_health_score():
    """演示健康评分功能"""
    print("\n" + "="*60)
    print("💚 性能监控演示 - 健康评分")
    print("="*60)

    monitor = PerformanceMonitor()

    print("📊 启动监控并计算健康评分...")
    monitor.start_monitoring(interval=1.0)

    print("⏳ 监控中... (10秒)")
    for i in range(10):
        time.sleep(1)
        score = monitor.get_system_health_score()
        metrics = monitor.get_current_metrics()

        print(f"   健康评分: {score:.1f}/100")
        print(f"   CPU: {metrics.get('cpu', {}).get('percent', 0):.1f}% "
              f"内存: {metrics.get('memory', {}).get('percent', 0):.1f}%")

        # 健康评分解释
        if score >= 80:
            status = "🟢 健康"
        elif score >= 60:
            status = "🟡 一般"
        else:
            status = "🔴 不良"
        print(f"   状态: {status}")

    monitor.stop_monitoring()

    return monitor

def demonstrate_threshold_management():
    """演示阈值管理功能"""
    print("\n" + "="*60)
    print("⚙️  性能监控演示 - 阈值管理")
    print("="*60)

    monitor = PerformanceMonitor()

    print("📊 当前阈值设置:")
    for key, value in monitor.thresholds.items():
        print(f"   {key}: {value}")

    print("\n🔧 更新阈值...")
    monitor.set_threshold('cpu_percent', 75.0)
    monitor.set_threshold('memory_percent', 80.0)
    monitor.set_threshold('disk_usage_percent', 85.0)

    print("📊 更新后的阈值:")
    for key, value in monitor.thresholds.items():
        print(f"   {key}: {value}")

    return monitor

def main():
    """主函数"""
    print("🎯 性能监控系统演示")
    print("="*60)
    print("这个演示将展示性能监控系统的各项功能")
    print("包括: 基本监控、告警系统、性能报告、健康评分、阈值管理")
    print("")
    print("🔋 资源优化特性:")
    print("  • 按需启动: 默认不自动监控，节省资源")
    print("  • 智能停止: 检测用户活动和页面状态")
    print("  • 优化频率: 5秒更新间隔，减少资源消耗")
    print("  • 自动清理: 页面卸载时自动停止并清理资源")
    print("="*60)

    setup_logging()

    try:
        # 演示各项功能
        demonstrate_basic_monitoring()
        demonstrate_alerts()
        demonstrate_reporting()
        demonstrate_health_score()
        demonstrate_threshold_management()

        print("\n" + "="*60)
        print("✅ 性能监控演示完成!")
        print("="*60)
        print("🎉 所有功能演示成功")
        print("💡 提示: 可以通过Web界面查看实时性能监控")
        print("🔋 新特性: 性能监控现在采用按需启动模式，更节省资源!")

    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        logging.error(f"演示错误: {e}", exc_info=True)

if __name__ == "__main__":
    main()
