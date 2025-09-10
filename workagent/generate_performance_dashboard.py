#!/usr/bin/env python3
"""
性能监控仪表板生成器
生成系统性能监控的图表和报告
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import os
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.performance_monitor import PerformanceMonitor

class PerformanceDashboard:
    """性能监控仪表板生成器"""

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_dashboard(self, minutes=60):
        """生成完整的性能监控仪表板"""
        print("📊 生成性能监控仪表板...")

        # 启动监控收集数据
        print("📈 收集性能数据...")
        self.monitor.start_monitoring(interval=1.0)

        # 等待数据收集
        import time
        print(f"⏳ 收集数据中... ({minutes}分钟)")
        for i in range(minutes * 6):  # 每10秒一个数据点
            time.sleep(10)
            if i % 6 == 0:
                print(f"   已收集 {i//6 + 1} 分钟数据...")

        self.monitor.stop_monitoring()

        # 生成图表
        self._create_performance_chart(minutes)
        self._create_resource_usage_chart(minutes)
        self._create_health_trend_chart(minutes)

        # 生成报告
        self._generate_text_report(minutes)

        print("✅ 仪表板生成完成!")
        print(f"📁 报告保存位置: {self.reports_dir}")

    def _create_performance_chart(self, minutes):
        """创建性能趋势图"""
        print("📈 生成性能趋势图...")

        history = self.monitor.get_metrics_history(minutes)
        if not history:
            print("❌ 没有足够的性能数据")
            return

        # 准备数据
        timestamps = [m['timestamp'] for m in history]
        cpu_data = [m['cpu']['percent'] for m in history]
        memory_data = [m['memory']['percent'] for m in history]
        disk_data = [m['disk']['percent'] for m in history]

        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'系统性能监控 - 最近{minutes}分钟', fontsize=16, fontweight='bold')

        # CPU使用率
        ax1.plot(timestamps, cpu_data, 'r-', linewidth=2, label='CPU使用率')
        ax1.set_title('CPU使用率趋势')
        ax1.set_ylabel('使用率 (%)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 内存使用率
        ax2.plot(timestamps, memory_data, 'b-', linewidth=2, label='内存使用率')
        ax2.set_title('内存使用率趋势')
        ax2.set_ylabel('使用率 (%)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # 磁盘使用率
        ax3.plot(timestamps, disk_data, 'g-', linewidth=2, label='磁盘使用率')
        ax3.set_title('磁盘使用率趋势')
        ax3.set_ylabel('使用率 (%)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # 综合健康评分
        health_scores = []
        for m in history:
            score = 100.0
            score = min(score, 100 - m['cpu']['percent'])
            score = min(score, 100 - m['memory']['percent'])
            score = min(score, 100 - m['disk']['percent'])
            health_scores.append(score)

        ax4.plot(timestamps, health_scores, 'purple', linewidth=2, label='健康评分')
        ax4.set_title('系统健康评分趋势')
        ax4.set_ylabel('健康评分 (0-100)')
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        # 设置X轴格式
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"performance_dashboard_{timestamp}.png"
        filepath = self.reports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ 性能趋势图已保存: {filepath}")

    def _create_resource_usage_chart(self, minutes):
        """创建资源使用情况饼图"""
        print("📊 生成资源使用情况图...")

        current_metrics = self.monitor.get_current_metrics()
        if 'error' in current_metrics:
            print("❌ 无法获取当前指标")
            return

        # 准备数据
        labels = ['CPU使用', 'CPU空闲', '内存使用', '内存空闲', '磁盘使用', '磁盘空闲']
        cpu_used = current_metrics['cpu']['percent']
        cpu_free = 100 - cpu_used
        memory_used = current_metrics['memory']['percent']
        memory_free = 100 - memory_used
        disk_used = current_metrics['disk']['percent']
        disk_free = 100 - disk_used

        sizes = [cpu_used, cpu_free, memory_used, memory_free, disk_used, disk_free]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#99ccff']

        # 创建饼图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('系统资源使用情况', fontsize=16, fontweight='bold')

        # CPU使用情况
        ax1.pie([cpu_used, cpu_free], labels=['使用', '空闲'], colors=['#ff9999', '#66b3ff'],
                autopct='%1.1f%%', startangle=90)
        ax1.set_title('CPU使用情况')

        # 内存使用情况
        ax2.pie([memory_used, memory_free], labels=['使用', '空闲'], colors=['#99ff99', '#ffcc99'],
                autopct='%1.1f%%', startangle=90)
        ax2.set_title('内存使用情况')

        # 磁盘使用情况
        ax3.pie([disk_used, disk_free], labels=['使用', '空闲'], colors=['#ff99cc', '#99ccff'],
                autopct='%1.1f%%', startangle=90)
        ax3.set_title('磁盘使用情况')

        # 资源使用率条形图
        resources = ['CPU', '内存', '磁盘']
        usage = [cpu_used, memory_used, disk_used]
        colors_bar = ['#ff9999', '#99ff99', '#ff99cc']

        bars = ax4.bar(resources, usage, color=colors_bar, alpha=0.7)
        ax4.set_title('资源使用率对比')
        ax4.set_ylabel('使用率 (%)')
        ax4.set_ylim(0, 100)

        # 添加数值标签
        for bar, value in zip(bars, usage):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom')

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"resource_usage_{timestamp}.png"
        filepath = self.reports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ 资源使用情况图已保存: {filepath}")

    def _create_health_trend_chart(self, minutes):
        """创建健康趋势分析图"""
        print("💚 生成健康趋势分析图...")

        history = self.monitor.get_metrics_history(minutes)
        if not history:
            print("❌ 没有足够的性能数据")
            return

        # 计算健康评分历史
        timestamps = []
        health_scores = []
        cpu_scores = []
        memory_scores = []
        disk_scores = []

        for m in history:
            timestamps.append(m['timestamp'])
            cpu_score = max(0, 100 - m['cpu']['percent'])
            memory_score = max(0, 100 - m['memory']['percent'])
            disk_score = max(0, 100 - m['disk']['percent'])
            health_score = min(cpu_score, memory_score, disk_score)

            cpu_scores.append(cpu_score)
            memory_scores.append(memory_score)
            disk_scores.append(disk_score)
            health_scores.append(health_score)

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('系统健康趋势分析', fontsize=16, fontweight='bold')

        # 健康评分趋势
        ax1.plot(timestamps, health_scores, 'purple', linewidth=3, label='综合健康评分', marker='o')
        ax1.fill_between(timestamps, 0, health_scores, alpha=0.3, color='purple')
        ax1.set_title('综合健康评分趋势')
        ax1.set_ylabel('健康评分 (0-100)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 添加健康状态区域
        ax1.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='健康阈值')
        ax1.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='警告阈值')
        ax1.axhline(y=40, color='red', linestyle='--', alpha=0.5, label='危险阈值')

        # 各组件健康评分
        ax2.plot(timestamps, cpu_scores, 'r-', linewidth=2, label='CPU健康评分', alpha=0.8)
        ax2.plot(timestamps, memory_scores, 'b-', linewidth=2, label='内存健康评分', alpha=0.8)
        ax2.plot(timestamps, disk_scores, 'g-', linewidth=2, label='磁盘健康评分', alpha=0.8)
        ax2.set_title('各组件健康评分')
        ax2.set_ylabel('健康评分 (0-100)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # 设置X轴格式
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"health_trend_{timestamp}.png"
        filepath = self.reports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ 健康趋势分析图已保存: {filepath}")

    def _generate_text_report(self, minutes):
        """生成文本报告"""
        print("📝 生成文本报告...")

        report = self.monitor.get_performance_report(minutes)
        current_metrics = self.monitor.get_current_metrics()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"performance_report_{timestamp}.txt"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("系统性能监控报告\n")
            f.write("="*60 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"监控周期: 最近 {minutes} 分钟\n")
            f.write("\n")

            if 'error' in report:
                f.write(f"错误: {report['error']}\n")
            else:
                f.write("📊 性能统计\n")
                f.write("-"*30 + "\n")
                f.write(f"数据点数量: {report['data_points']}\n")
                f.write(f"告警数量: {report['alerts_count']}\n")
                f.write(f"整体趋势: {report['trend']}\n")
                f.write("\n")

                f.write("📈 平均使用率\n")
                f.write("-"*20 + "\n")
                avg_cpu = report.get('avg_cpu', 0.0)
                avg_mem = report.get('avg_memory', 0.0)
                avg_disk = report.get('avg_disk', 0.0)
                f.write(f"CPU 平均: {avg_cpu:.1f}%  内存 平均: {avg_mem:.1f}%  磁盘 平均: {avg_disk:.1f}%\n")

                f.write("📉 峰值使用率\n")
                f.write("-"*20 + "\n")
                peak_cpu = report.get('peak_cpu', 0.0)
                peak_mem = report.get('peak_memory', 0.0)
                peak_disk = report.get('peak_disk', 0.0)
                f.write(f"CPU 峰值: {peak_cpu:.1f}%  内存 峰值: {peak_mem:.1f}%  磁盘 峰值: {peak_disk:.1f}%\n")

                f.write("💻 当前系统状态\n")
            f.write("-"*20 + "\n")
            if 'error' in current_metrics:
                f.write(f"错误: {current_metrics['error']}\n")
            else:
                cpu_now = current_metrics.get('cpu', {}).get('percent', 0.0)
                mem_now = current_metrics.get('memory', {}).get('percent', 0.0)
                disk_now = current_metrics.get('disk', {}).get('percent', 0.0)
                f.write(f"CPU: {cpu_now:.1f}%  内存: {mem_now:.1f}%  磁盘: {disk_now:.1f}%\n")

            f.write("🚨 最近告警\n")
            f.write("-"*15 + "\n")
            alerts = self.monitor.alerts[-5:]  # 最近5个告警
            if alerts:
                for alert in alerts:
                    f.write(f"{alert['timestamp'].strftime('%H:%M:%S')}: {alert['message']}\n")
            else:
                f.write("暂无告警\n")

            f.write("\n" + "="*60 + "\n")

        print(f"✅ 文本报告已保存: {filepath}")

def main():
    """主函数"""
    print("🎯 性能监控仪表板生成器")
    print("="*60)

    try:
        dashboard = PerformanceDashboard()

        # 生成仪表板（默认1小时）
        dashboard.generate_dashboard(minutes=60)

        print("\n" + "="*60)
        print("✅ 仪表板生成完成!")
        print("="*60)
        print("📁 生成的文件:")
        reports_dir = Path("reports")
        for file in reports_dir.glob("*"):
            if file.is_file():
                print(f"   {file.name}")

    except KeyboardInterrupt:
        print("\n⏹️  生成过程被用户中断")
    except Exception as e:
        print(f"\n❌ 生成过程中出现错误: {e}")

if __name__ == "__main__":
    main()
