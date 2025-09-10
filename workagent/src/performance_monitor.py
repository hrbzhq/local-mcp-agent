import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import logging
from collections import deque

class PerformanceMonitor:
    """性能监控模块"""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.is_monitoring = False
        self.monitor_thread = None
        self.alerts = []
        self.alert_callbacks = []

        # 性能阈值设置
        self.thresholds = {
            'cpu_percent': 80.0,      # CPU使用率阈值
            'memory_percent': 85.0,   # 内存使用率阈值
            'disk_usage_percent': 90.0,  # 磁盘使用率阈值
            'response_time': 5.0,     # 响应时间阈值（秒）
            'error_rate': 0.1         # 错误率阈值
        }

    def start_monitoring(self, interval: float = 1.0):
        """启动性能监控"""
        if self.is_monitoring:
            logging.warning("性能监控已在运行")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logging.info(f"性能监控已启动，监控间隔: {interval}秒")

    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logging.info("性能监控已停止")

    def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                self.check_alerts(metrics)
                time.sleep(interval)
            except Exception as e:
                logging.error(f"性能监控错误: {e}")
                time.sleep(interval)

    def collect_metrics(self) -> Dict[str, Any]:
        """收集系统性能指标"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # 内存信息
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB

            # 磁盘信息
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB

            # 网络信息
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent / (1024**2)  # MB
            bytes_recv = network.bytes_recv / (1024**2)  # MB

            # 进程信息
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024**2)  # MB
            process_cpu = process.cpu_percent()

            # 系统负载
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)

            metrics = {
                'timestamp': datetime.now(),
                'cpu': {
                    'percent': cpu_percent,
                    'load_avg': load_avg
                },
                'memory': {
                    'percent': memory_percent,
                    'used_gb': memory_used,
                    'total_gb': memory_total
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': disk_used,
                    'total_gb': disk_total
                },
                'network': {
                    'bytes_sent_mb': bytes_sent,
                    'bytes_recv_mb': bytes_recv
                },
                'process': {
                    'memory_mb': process_memory,
                    'cpu_percent': process_cpu
                }
            }

            return metrics

        except Exception as e:
            logging.error(f"收集性能指标失败: {e}")
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }

    def check_alerts(self, metrics: Dict[str, Any]):
        """检查性能告警"""
        if 'error' in metrics:
            return

        alerts = []

        # CPU使用率告警
        if metrics['cpu']['percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"CPU使用率过高: {metrics['cpu']['percent']:.1f}%",
                'value': metrics['cpu']['percent'],
                'threshold': self.thresholds['cpu_percent'],
                'timestamp': metrics['timestamp']
            })

        # 内存使用率告警
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'message': f"内存使用率过高: {metrics['memory']['percent']:.1f}%",
                'value': metrics['memory']['percent'],
                'threshold': self.thresholds['memory_percent'],
                'timestamp': metrics['timestamp']
            })

        # 磁盘使用率告警
        if metrics['disk']['percent'] > self.thresholds['disk_usage_percent']:
            alerts.append({
                'type': 'disk_high',
                'message': f"磁盘使用率过高: {metrics['disk']['percent']:.1f}%",
                'value': metrics['disk']['percent'],
                'threshold': self.thresholds['disk_usage_percent'],
                'timestamp': metrics['timestamp']
            })

        # 添加到告警列表
        self.alerts.extend(alerts)

        # 保留最近100个告警
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # 触发告警回调
        for alert in alerts:
            self._trigger_alert_callbacks(alert)

    def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """触发告警回调"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logging.error(f"告警回调执行失败: {e}")

    def add_alert_callback(self, callback):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        else:
            return self.collect_metrics()

    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """获取指定时间范围内的性能历史"""
        if not self.metrics_history:
            return []

        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        history = []

        for metrics in self.metrics_history:
            if metrics['timestamp'] > cutoff_time:
                history.append(metrics)

        return history

    def get_performance_report(self, minutes: int = 60) -> Dict[str, Any]:
        """生成性能报告"""
        history = self.get_metrics_history(minutes)

        if not history:
            return {'error': '没有足够的性能数据'}

        # 计算平均值
        cpu_avg = sum(m['cpu']['percent'] for m in history) / len(history)
        memory_avg = sum(m['memory']['percent'] for m in history) / len(history)
        disk_avg = sum(m['disk']['percent'] for m in history) / len(history)

        # 计算峰值
        cpu_peak = max(m['cpu']['percent'] for m in history)
        memory_peak = max(m['memory']['percent'] for m in history)
        disk_peak = max(m['disk']['percent'] for m in history)

        # 计算趋势
        recent_avg = sum(m['cpu']['percent'] for m in history[-10:]) / min(10, len(history))
        trend = "上升" if recent_avg > cpu_avg else "下降" if recent_avg < cpu_avg else "稳定"

        return {
            'period_minutes': minutes,
            'data_points': len(history),
            'averages': {
                'cpu_percent': cpu_avg,
                'memory_percent': memory_avg,
                'disk_percent': disk_avg
            },
            'peaks': {
                'cpu_percent': cpu_peak,
                'memory_percent': memory_peak,
                'disk_percent': disk_peak
            },
            'trend': trend,
            'alerts_count': len([a for a in self.alerts if a['timestamp'] > datetime.now() - timedelta(minutes=minutes)]),
            'current_metrics': self.get_current_metrics()
        }

    def set_threshold(self, metric: str, value: float):
        """设置性能阈值"""
        if metric in self.thresholds:
            self.thresholds[metric] = value
            logging.info(f"性能阈值已更新: {metric} = {value}")
        else:
            logging.warning(f"未知的性能指标: {metric}")

    def get_system_health_score(self) -> float:
        """计算系统健康评分 (0-100)"""
        metrics = self.get_current_metrics()

        if 'error' in metrics:
            return 0.0

        score = 100.0

        # CPU健康评分
        cpu_score = max(0, 100 - metrics['cpu']['percent'])
        score = min(score, cpu_score)

        # 内存健康评分
        memory_score = max(0, 100 - metrics['memory']['percent'])
        score = min(score, memory_score)

        # 磁盘健康评分
        disk_score = max(0, 100 - metrics['disk']['percent'])
        score = min(score, disk_score)

        return score
