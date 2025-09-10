import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

class DataVisualizer:
    """数据可视化模块"""

    def __init__(self, output_dir: str = 'reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 设置matplotlib参数
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def create_performance_dashboard(self, performance_data: Dict[str, Any],
                                   time_range: int = 60) -> str:
        """创建性能监控仪表板"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'系统性能监控仪表板 (最近{time_range}分钟)', fontsize=16)

            # CPU使用率
            if 'cpu_history' in performance_data:
                cpu_data = performance_data['cpu_history']
                axes[0, 0].plot(cpu_data['timestamps'], cpu_data['values'], 'b-', linewidth=2)
                axes[0, 0].set_title('CPU使用率 (%)')
                axes[0, 0].set_ylabel('使用率 (%)')
                axes[0, 0].grid(True, alpha=0.3)

            # 内存使用率
            if 'memory_history' in performance_data:
                memory_data = performance_data['memory_history']
                axes[0, 1].plot(memory_data['timestamps'], memory_data['values'], 'g-', linewidth=2)
                axes[0, 1].set_title('内存使用率 (%)')
                axes[0, 1].set_ylabel('使用率 (%)')
                axes[0, 1].grid(True, alpha=0.3)

            # 磁盘使用率
            if 'disk_history' in performance_data:
                disk_data = performance_data['disk_history']
                axes[1, 0].plot(disk_data['timestamps'], disk_data['values'], 'r-', linewidth=2)
                axes[1, 0].set_title('磁盘使用率 (%)')
                axes[1, 0].set_ylabel('使用率 (%)')
                axes[1, 0].grid(True, alpha=0.3)

            # 网络流量
            if 'network_history' in performance_data:
                network_data = performance_data['network_history']
                axes[1, 1].plot(network_data['timestamps'], network_data['sent'], 'c-', label='发送', linewidth=2)
                axes[1, 1].plot(network_data['timestamps'], network_data['recv'], 'm-', label='接收', linewidth=2)
                axes[1, 1].set_title('网络流量 (MB)')
                axes[1, 1].set_ylabel('流量 (MB)')
                axes[1, 1].legend()
                axes[1, 1].grid(True, alpha=0.3)

            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'performance_dashboard_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            logging.info(f"性能仪表板已生成: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"生成性能仪表板失败: {e}")
            return None

    def create_task_analysis_report(self, task_data: Dict[str, Any]) -> str:
        """创建任务分析报告"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('任务执行分析报告', fontsize=16)

            # 任务类型分布
            if 'task_types' in task_data:
                task_types = task_data['task_types']
                if task_types:
                    axes[0, 0].pie(task_types.values(), labels=task_types.keys(), autopct='%1.1f%%')
                    axes[0, 0].set_title('任务类型分布')

            # 模型使用统计
            if 'model_usage' in task_data:
                model_usage = task_data['model_usage']
                if model_usage:
                    axes[0, 1].bar(model_usage.keys(), model_usage.values())
                    axes[0, 1].set_title('模型使用统计')
                    axes[0, 1].set_ylabel('使用次数')
                    plt.setp(axes[0, 1].get_xticklabels(), rotation=45)

            # 执行时间分布
            if 'execution_times' in task_data:
                exec_times = task_data['execution_times']
                if exec_times:
                    axes[1, 0].hist(exec_times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                    axes[1, 0].set_title('任务执行时间分布')
                    axes[1, 0].set_xlabel('执行时间 (秒)')
                    axes[1, 0].set_ylabel('任务数量')

            # 成功率趋势
            if 'success_trend' in task_data:
                success_trend = task_data['success_trend']
                if success_trend:
                    axes[1, 1].plot(success_trend['dates'], success_trend['rates'], 'g-', linewidth=2)
                    axes[1, 1].set_title('任务成功率趋势')
                    axes[1, 1].set_ylabel('成功率 (%)')
                    axes[1, 1].set_ylim(0, 100)

            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'task_analysis_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            logging.info(f"任务分析报告已生成: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"生成任务分析报告失败: {e}")
            return None

    def create_system_health_chart(self, health_score: float,
                                 metrics: Dict[str, Any]) -> str:
        """创建系统健康状态图表"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # 健康评分仪表盘
            ax1.pie([health_score, 100-health_score],
                   labels=['健康', '异常'],
                   colors=['#4CAF50', '#F44336'],
                   autopct='%1.1f%%',
                   startangle=90)
            ax1.set_title(f'系统健康评分: {health_score:.1f}/100')

            # 各项指标雷达图
            if metrics:
                categories = list(metrics.keys())
                values = [metrics[cat] for cat in categories]

                # 闭合雷达图
                values += values[:1]
                categories += categories[:1]

                angles = [n / float(len(categories)-1) * 2 * 3.14159 for n in range(len(categories))]
                ax2.plot(angles, values, 'o-', linewidth=2, label='当前值')
                ax2.fill(angles, values, alpha=0.25)
                ax2.set_xticks(angles[:-1])
                ax2.set_xticklabels(categories[:-1])
                ax2.set_ylim(0, 100)
                ax2.set_title('系统指标雷达图')
                ax2.grid(True)

            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'system_health_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            logging.info(f"系统健康图表已生成: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"生成系统健康图表失败: {e}")
            return None

    def create_model_comparison_chart(self, model_stats: Dict[str, Any]) -> str:
        """创建模型对比图表"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('模型性能对比分析', fontsize=16)

            # 响应时间对比
            if 'response_times' in model_stats:
                models = list(model_stats['response_times'].keys())
                times = list(model_stats['response_times'].values())
                axes[0, 0].bar(models, times, color='skyblue', alpha=0.7)
                axes[0, 0].set_title('平均响应时间 (秒)')
                axes[0, 0].set_ylabel('时间 (秒)')
                plt.setp(axes[0, 0].get_xticklabels(), rotation=45)

            # 成功率对比
            if 'success_rates' in model_stats:
                models = list(model_stats['success_rates'].keys())
                rates = list(model_stats['success_rates'].values())
                axes[0, 1].bar(models, rates, color='lightgreen', alpha=0.7)
                axes[0, 1].set_title('成功率 (%)')
                axes[0, 1].set_ylabel('成功率 (%)')
                axes[0, 1].set_ylim(0, 100)
                plt.setp(axes[0, 1].get_xticklabels(), rotation=45)

            # 使用频率对比
            if 'usage_counts' in model_stats:
                models = list(model_stats['usage_counts'].keys())
                counts = list(model_stats['usage_counts'].values())
                axes[1, 0].pie(counts, labels=models, autopct='%1.1f%%')
                axes[1, 0].set_title('使用频率分布')

            # 错误类型分析
            if 'error_types' in model_stats:
                error_types = model_stats['error_types']
                if error_types:
                    types = list(error_types.keys())
                    counts = list(error_types.values())
                    axes[1, 1].barh(types, counts, color='salmon', alpha=0.7)
                    axes[1, 1].set_title('错误类型统计')
                    axes[1, 1].set_xlabel('错误次数')

            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'model_comparison_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            logging.info(f"模型对比图表已生成: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"生成模型对比图表失败: {e}")
            return None

    def generate_html_report(self, data: Dict[str, Any],
                           template: str = 'comprehensive') -> str:
        """生成HTML报告"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>多模型智能Agent系统报告</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e8f4f8; border-radius: 3px; }}
                    .chart {{ text-align: center; margin: 20px 0; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 多模型智能Agent系统报告</h1>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="section">
                    <h2>📊 系统概览</h2>
                    <div class="metric">总任务数: {data.get('total_tasks', 0)}</div>
                    <div class="metric">平均响应时间: {data.get('avg_response_time', 0):.2f}秒</div>
                    <div class="metric">成功率: {data.get('success_rate', 0):.1f}%</div>
                    <div class="metric">系统健康评分: {data.get('health_score', 0):.1f}/100</div>
                </div>

                <div class="section">
                    <h2>🔧 性能指标</h2>
                    <table>
                        <tr><th>指标</th><th>当前值</th><th>平均值</th><th>峰值</th></tr>
                        <tr><td>CPU使用率</td><td>{data.get('cpu_current', 0):.1f}%</td><td>{data.get('cpu_avg', 0):.1f}%</td><td>{data.get('cpu_peak', 0):.1f}%</td></tr>
                        <tr><td>内存使用率</td><td>{data.get('memory_current', 0):.1f}%</td><td>{data.get('memory_avg', 0):.1f}%</td><td>{data.get('memory_peak', 0):.1f}%</td></tr>
                        <tr><td>磁盘使用率</td><td>{data.get('disk_current', 0):.1f}%</td><td>{data.get('disk_avg', 0):.1f}%</td><td>{data.get('disk_peak', 0):.1f}%</td></tr>
                    </table>
                </div>

                <div class="section">
                    <h2>📈 图表展示</h2>
                    <p>详细图表请查看附件图片文件</p>
                </div>

                <div class="section">
                    <h2>⚠️ 系统告警</h2>
                    <p>告警数量: {data.get('alerts_count', 0)}</p>
                    {self._generate_alerts_html(data.get('alerts', []))}
                </div>
            </body>
            </html>
            """

            # 保存HTML报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'system_report_{timestamp}.html'
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logging.info(f"HTML报告已生成: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"生成HTML报告失败: {e}")
            return None

    def _generate_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """生成告警HTML"""
        if not alerts:
            return "<p>暂无告警</p>"

        html = "<table><tr><th>时间</th><th>类型</th><th>消息</th><th>值</th></tr>"
        for alert in alerts[-10:]:  # 只显示最近10个告警
            html += f"""
            <tr>
                <td>{alert.get('timestamp', '')}</td>
                <td>{alert.get('type', '')}</td>
                <td>{alert.get('message', '')}</td>
                <td>{alert.get('value', '')}</td>
            </tr>
            """
        html += "</table>"
        return html

    def export_data_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """导出数据到CSV文件"""
        try:
            # 将数据转换为DataFrame
            df_data = {}
            for key, value in data.items():
                if isinstance(value, (list, tuple)):
                    df_data[key] = value
                elif isinstance(value, dict):
                    # 展平嵌套字典
                    for sub_key, sub_value in value.items():
                        df_data[f"{key}_{sub_key}"] = sub_value if isinstance(sub_value, (list, tuple)) else [sub_value]
                else:
                    df_data[key] = [value]

            # 创建DataFrame并保存
            df = pd.DataFrame(df_data)
            filepath = os.path.join(self.output_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')

            logging.info(f"数据已导出到CSV: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"导出CSV失败: {e}")
            return None
