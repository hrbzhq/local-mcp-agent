"""
资源管理器 - Resource Manager for Autonomous Optimization
"""

import psutil
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import threading

class ResourceManager:
    """资源管理器"""

    def __init__(self):
        self.monitoring_active = False
        self.resource_history = deque(maxlen=1000)  # 保留最近1000个数据点
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'network_connections': 100
        }

        # 优化时间窗口配置（小时）
        self.optimization_windows = {
            'cpu_optimization': {'start': 18, 'end': 9},  # 18:00-次日9:00
            'memory_optimization': {'start': 18, 'end': 9},  # 18:00-次日9:00
            'disk_optimization': {'start': 18, 'end': 9},  # 18:00-次日9:00
            'network_optimization': {'start': 2, 'end': 4}  # 凌晨2:00-4:00
        }

        self.optimization_strategies = {
            'cpu_high': self._optimize_cpu_usage,
            'memory_high': self._optimize_memory_usage,
            'disk_high': self._optimize_disk_usage,
            'network_high': self._optimize_network_usage
        }

    def set_optimization_window(self, optimization_type: str, start_hour: int, end_hour: int):
        """设置优化时间窗口"""
        if optimization_type in self.optimization_windows:
            self.optimization_windows[optimization_type] = {'start': start_hour, 'end': end_hour}
            logging.info(f"已更新 {optimization_type} 的优化时间窗口: {start_hour}:00 - {end_hour}:00")
        else:
            logging.warning(f"未知的优化类型: {optimization_type}")

    def _is_optimization_window(self, optimization_type: str) -> bool:
        """检查当前时间是否在指定的优化时间窗口内"""
        from datetime import datetime

        if optimization_type not in self.optimization_windows:
            return False

        current_hour = datetime.now().hour
        window = self.optimization_windows[optimization_type]

        if window['start'] <= window['end']:
            # 同一日期内的窗口，如 9:00-18:00
            return window['start'] <= current_hour < window['end']
        else:
            # 跨日期的窗口，如 18:00-次日9:00
            return current_hour >= window['start'] or current_hour < window['end']

    def get_optimization_windows(self) -> Dict[str, Dict[str, int]]:
        """获取所有优化时间窗口配置"""
        return self.optimization_windows.copy()

    def start_monitoring(self):
        """启动资源监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitoring_thread.start()
            logging.info("资源监控已启动")

    def stop_monitoring(self):
        """停止资源监控"""
        self.monitoring_active = False
        logging.info("资源监控已停止")

    def _monitoring_loop(self):
        """监控主循环"""
        while self.monitoring_active:
            try:
                # 收集资源使用情况
                resource_data = self._collect_resource_data()

                # 存储历史数据
                self.resource_history.append(resource_data)

                # 检查阈值并触发警报
                self._check_thresholds(resource_data)

                # 执行自动优化
                self._execute_auto_optimization(resource_data)

                time.sleep(10)  # 每10秒检查一次

            except Exception as e:
                logging.error(f"资源监控出错: {e}")
                time.sleep(30)  # 出错后等待30秒

    def _collect_resource_data(self) -> Dict[str, Any]:
        """收集资源使用数据"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent,
                    'used': psutil.virtual_memory().used
                },
                'disk': {
                    'total': psutil.disk_usage('C:\\').total,
                    'free': psutil.disk_usage('C:\\').free,
                    'percent': psutil.disk_usage('C:\\').percent
                },
                'network': {
                    'connections': len(psutil.net_connections()),
                    'bytes_sent': psutil.net_io_counters().bytes_sent,
                    'bytes_recv': psutil.net_io_counters().bytes_recv
                },
                'processes': {
                    'count': len(psutil.pids()),
                    'top_cpu': self._get_top_processes('cpu', 5),
                    'top_memory': self._get_top_processes('memory', 5)
                }
            }
        except Exception as e:
            logging.error(f"收集资源数据失败: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _get_top_processes(self, sort_by: str, limit: int) -> List[Dict[str, Any]]:
        """获取资源消耗最高的进程"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'memory_percent': proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)

            return processes[:limit]
        except Exception as e:
            logging.error(f"获取进程信息失败: {e}")
            return []

    def _check_thresholds(self, resource_data: Dict[str, Any]):
        """检查资源阈值"""
        alerts = []

        # CPU检查
        if resource_data.get('cpu', {}).get('percent', 0) > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'level': 'warning',
                'message': f"CPU使用率过高: {resource_data['cpu']['percent']:.1f}%",
                'timestamp': resource_data['timestamp']
            })

        # 内存检查
        if resource_data.get('memory', {}).get('percent', 0) > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'level': 'warning',
                'message': f"内存使用率过高: {resource_data['memory']['percent']:.1f}%",
                'timestamp': resource_data['timestamp']
            })

        # 磁盘检查
        if resource_data.get('disk', {}).get('percent', 0) > self.thresholds['disk_percent']:
            alerts.append({
                'type': 'disk_high',
                'level': 'critical',
                'message': f"磁盘使用率过高: {resource_data['disk']['percent']:.1f}%",
                'timestamp': resource_data['timestamp']
            })

        # 网络连接检查
        if resource_data.get('network', {}).get('connections', 0) > self.thresholds['network_connections']:
            alerts.append({
                'type': 'network_high',
                'level': 'info',
                'message': f"网络连接数过多: {resource_data['network']['connections']}",
                'timestamp': resource_data['timestamp']
            })

        # 添加警报到队列
        self.alerts.extend(alerts)

        # 只保留最近100个警报
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # 记录严重警报
        for alert in alerts:
            if alert['level'] in ['warning', 'critical']:
                logging.warning(f"资源警报: {alert['message']}")

    def _execute_auto_optimization(self, resource_data: Dict[str, Any]):
        """执行自动优化"""
        for alert in self.alerts[-5:]:  # 检查最近5个警报
            if alert['type'] in self.optimization_strategies:
                try:
                    optimization_func = self.optimization_strategies[alert['type']]
                    optimization_func(resource_data)
                except Exception as e:
                    logging.error(f"执行自动优化失败 ({alert['type']}): {e}")

    def _optimize_cpu_usage(self, resource_data: Dict[str, Any]):
        """优化CPU使用"""
        if not self._is_optimization_window('cpu_optimization'):
            return

        logging.info("执行CPU优化")

        # 降低非关键进程优先级
        try:
            top_cpu_processes = resource_data.get('processes', {}).get('top_cpu', [])
            for proc_info in top_cpu_processes[:2]:  # 只处理前2个高CPU进程
                try:
                    proc = psutil.Process(proc_info['pid'])
                    # 如果不是系统关键进程，降低优先级
                    if proc_info['cpu_percent'] > 50 and not self._is_system_process(proc_info['name']):
                        current_nice = proc.nice()
                        if current_nice < 10:  # 降低优先级
                            proc.nice(current_nice + 1)
                            logging.info(f"降低进程 {proc_info['name']} (PID: {proc_info['pid']}) 优先级")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logging.error(f"CPU优化失败: {e}")

    def _optimize_memory_usage(self, resource_data: Dict[str, Any]):
        """优化内存使用"""
        if not self._is_optimization_window('memory_optimization'):
            return

        logging.info("执行内存优化")

        # 建议清理缓存或重启服务
        memory_percent = resource_data.get('memory', {}).get('percent', 0)
        if memory_percent > 90:
            logging.warning("内存使用率严重过高，建议重启相关服务")
            # 这里可以添加自动重启逻辑，但需要谨慎

    def _optimize_disk_usage(self, resource_data: Dict[str, Any]):
        """优化磁盘使用"""
        if not self._is_optimization_window('disk_optimization'):
            return

        logging.info("执行磁盘优化")

        # 清理临时文件
        try:
            self._cleanup_temp_files()
        except Exception as e:
            logging.error(f"磁盘优化失败: {e}")

    def _optimize_network_usage(self, resource_data: Dict[str, Any]):
        """优化网络使用"""
        if not self._is_optimization_window('network_optimization'):
            return

        logging.info("执行网络优化")

        # 关闭不必要的连接
        try:
            connections = psutil.net_connections()
            if len(connections) > self.thresholds['network_connections']:
                logging.info(f"检测到 {len(connections)} 个网络连接，建议检查是否有异常连接")

                # 实际的网络优化逻辑
                self._perform_network_cleanup(connections)

        except Exception as e:
            logging.error(f"网络优化失败: {e}")

    def _is_system_process(self, process_name: str) -> bool:
        """判断是否为系统关键进程"""
        system_processes = [
            'systemd', 'init', 'kernel', 'launchd', 'svchost.exe',
            'lsass.exe', 'winlogon.exe', 'csrss.exe', 'smss.exe',
            'python', 'node', 'java'  # 我们自己的应用进程
        ]
        return any(sys_proc.lower() in process_name.lower() for sys_proc in system_processes)

    def _cleanup_temp_files(self):
        """清理临时文件"""
        import tempfile
        import shutil

        try:
            temp_dir = tempfile.gettempdir()
            total_cleaned = 0

            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        # 只删除超过1天的临时文件
                        if time.time() - os.path.getmtime(filepath) > 86400:
                            size = os.path.getsize(filepath)
                            os.remove(filepath)
                            total_cleaned += size
                except (OSError, PermissionError):
                    continue

            if total_cleaned > 0:
                logging.info(f"清理临时文件: {total_cleaned / 1024 / 1024:.1f} MB")

        except Exception as e:
            logging.error(f"清理临时文件失败: {e}")

    def get_resource_usage(self) -> Dict[str, Any]:
        """获取当前资源使用情况"""
        if self.resource_history:
            return self.resource_history[-1]
        else:
            return self._collect_resource_data()

    def get_resource_trends(self, hours: int = 1) -> Dict[str, Any]:
        """获取资源使用趋势"""
        if not self.resource_history:
            return {}

        # 计算时间范围内的数据
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [
            data for data in self.resource_history
            if datetime.fromisoformat(data['timestamp']) > cutoff_time
        ]

        if not recent_data:
            return {}

        # 计算趋势
        cpu_trend = self._calculate_trend([d.get('cpu', {}).get('percent', 0) for d in recent_data])
        memory_trend = self._calculate_trend([d.get('memory', {}).get('percent', 0) for d in recent_data])
        disk_trend = self._calculate_trend([d.get('disk', {}).get('percent', 0) for d in recent_data])

        return {
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'disk_trend': disk_trend,
            'data_points': len(recent_data),
            'time_range_hours': hours
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'stable'

        # 计算线性趋势
        n = len(values)
        if n < 2:
            return 'stable'

        # 简单趋势计算：比较前半部分和后半部分的平均值
        mid = n // 2
        first_half = values[:mid]
        second_half = values[mid:]

        if not first_half or not second_half:
            return 'stable'

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        diff = second_avg - first_avg

        if diff > 5:
            return 'increasing'
        elif diff < -5:
            return 'decreasing'
        else:
            return 'stable'

    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的警报"""
        return list(self.alerts)[-limit:] if self.alerts else []

    def set_threshold(self, resource_type: str, value: float):
        """设置资源阈值"""
        if resource_type in self.thresholds:
            self.thresholds[resource_type] = value
            logging.info(f"更新阈值: {resource_type} = {value}")

    def get_resource_report(self) -> Dict[str, Any]:
        """生成资源报告"""
        current_usage = self.get_resource_usage()
        trends = self.get_resource_trends(hours=1)
        alerts = self.get_alerts(limit=5)

        return {
            'current_usage': current_usage,
            'trends': trends,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(current_usage, trends, alerts),
            'generated_at': datetime.now().isoformat()
        }

    def _generate_recommendations(self, current_usage: Dict[str, Any],
                                trends: Dict[str, Any], alerts: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于当前使用情况的建议
        cpu_percent = current_usage.get('cpu', {}).get('percent', 0)
        memory_percent = current_usage.get('memory', {}).get('percent', 0)

        if cpu_percent > 80:
            recommendations.append("CPU使用率较高，考虑优化计算密集型任务")
        if memory_percent > 85:
            recommendations.append("内存使用率较高，考虑增加内存或优化内存使用")

        # 基于趋势的建议
        if trends.get('cpu_trend') == 'increasing':
            recommendations.append("CPU使用呈上升趋势，建议监控并准备扩容")
        if trends.get('memory_trend') == 'increasing':
            recommendations.append("内存使用呈上升趋势，建议检查内存泄漏")

        # 基于警报的建议
        critical_alerts = [alert for alert in alerts if alert.get('level') == 'critical']
        if critical_alerts:
            recommendations.append("存在严重资源警报，建议立即采取行动")

        return recommendations

    def _perform_network_cleanup(self, connections):
        """执行网络连接清理"""
        import signal

        cleaned_count = 0
        suspicious_connections = []

        for conn in connections:
            try:
                # 检查可疑连接
                if conn.status == 'ESTABLISHED':
                    # 检查是否为可疑端口或连接
                    if hasattr(conn, 'laddr') and hasattr(conn, 'raddr'):
                        local_port = conn.laddr.port if hasattr(conn.laddr, 'port') else None
                        remote_port = conn.raddr.port if hasattr(conn.raddr, 'raddr') and hasattr(conn.raddr, 'port') else None

                        # 可疑端口列表（可以根据需要调整）
                        suspicious_ports = [23, 25, 53, 80, 443, 3389, 5900]  # Telnet, SMTP, DNS, HTTP, HTTPS, RDP, VNC

                        if remote_port in suspicious_ports:
                            suspicious_connections.append(conn)

            except (AttributeError, TypeError):
                continue

        # 只清理少量可疑连接，避免影响系统稳定性
        for conn in suspicious_connections[:5]:  # 每次最多清理5个连接
            try:
                if hasattr(conn, 'pid') and conn.pid:
                    process = psutil.Process(conn.pid)
                    if not self._is_system_process(process.name()):
                        # 温和地终止进程
                        process.terminate()
                        cleaned_count += 1
                        logging.info(f"终止可疑进程: {process.name()} (PID: {conn.pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                logging.debug(f"无法终止进程: {e}")
                continue

        if cleaned_count > 0:
            logging.info(f"网络清理完成，共终止 {cleaned_count} 个可疑连接")
        else:
            logging.info("未发现需要清理的可疑网络连接")
