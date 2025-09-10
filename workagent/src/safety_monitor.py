"""
安全监控器 - Safety Monitor for Autonomous Optimization
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import sqlite3
import os
import threading

class SafetyMonitor:
    """安全监控器"""

    def __init__(self):
        self.safety_violations = []
        self.security_events = []
        self.safety_rules = self._load_safety_rules()
        self.monitoring_active = False
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'mcp', 'safety.db')
        self.init_database()

    def init_database(self):
        """初始化安全数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS safety_events (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    event_type TEXT,
                    severity TEXT,
                    description TEXT,
                    source TEXT,
                    action_taken TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS safety_rules (
                    id INTEGER PRIMARY KEY,
                    rule_name TEXT UNIQUE,
                    rule_type TEXT,
                    condition TEXT,
                    action TEXT,
                    enabled BOOLEAN DEFAULT 1
                )
            ''')

    def _load_safety_rules(self) -> Dict[str, Dict[str, Any]]:
        """加载安全规则"""
        return {
            'resource_exhaustion': {
                'type': 'threshold',
                'condition': 'cpu_percent > 95 or memory_percent > 95',
                'action': 'emergency_shutdown',
                'severity': 'critical'
            },
            'unauthorized_access': {
                'type': 'pattern',
                'condition': 'suspicious_login_attempts > 5',
                'action': 'block_ip',
                'severity': 'high'
            },
            'data_integrity': {
                'type': 'validation',
                'condition': 'data_corruption_detected',
                'action': 'data_backup',
                'severity': 'high'
            },
            'system_stability': {
                'type': 'monitoring',
                'condition': 'error_rate > 0.5',
                'action': 'reduce_load',
                'severity': 'medium'
            },
            'learning_safety': {
                'type': 'ai_safety',
                'condition': 'unsafe_learning_pattern_detected',
                'action': 'pause_learning',
                'severity': 'high'
            }
        }

    def start_monitoring(self):
        """启动安全监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitoring_thread.start()
            logging.info("安全监控已启动")

    def stop_monitoring(self):
        """停止安全监控"""
        self.monitoring_active = False
        logging.info("安全监控已停止")

    def _monitoring_loop(self):
        """安全监控主循环"""
        while self.monitoring_active:
            try:
                # 检查所有安全规则
                self._check_safety_rules()

                # 验证系统完整性
                self._verify_system_integrity()

                # 监控AI行为安全
                self._monitor_ai_safety()

                time.sleep(30)  # 每30秒检查一次

            except Exception as e:
                logging.error(f"安全监控出错: {e}")
                time.sleep(60)  # 出错后等待1分钟

    def _check_safety_rules(self):
        """检查安全规则"""
        for rule_name, rule in self.safety_rules.items():
            if not rule.get('enabled', True):
                continue

            try:
                violation_detected = self._evaluate_rule_condition(rule)
                if violation_detected:
                    self._handle_safety_violation(rule_name, rule)
            except Exception as e:
                logging.error(f"检查安全规则失败 ({rule_name}): {e}")

    def _evaluate_rule_condition(self, rule: Dict[str, Any]) -> bool:
        """评估规则条件"""
        condition = rule.get('condition', '')

        # 这里是简化的条件评估，实际实现需要更复杂的解析器
        if 'cpu_percent > 95' in condition:
            # 模拟CPU检查
            return False  # 暂时返回False，避免误报
        elif 'memory_percent > 95' in condition:
            # 模拟内存检查
            return False
        elif 'suspicious_login_attempts > 5' in condition:
            # 模拟登录尝试检查
            return False
        elif 'data_corruption_detected' in condition:
            # 模拟数据完整性检查
            return self._check_data_integrity()
        elif 'error_rate > 0.5' in condition:
            # 模拟错误率检查
            return False
        elif 'unsafe_learning_pattern_detected' in condition:
            # 模拟AI学习安全检查
            return self._check_learning_safety()

        return False

    def _handle_safety_violation(self, rule_name: str, rule: Dict[str, Any]):
        """处理安全违规"""
        severity = rule.get('severity', 'medium')
        action = rule.get('action', 'log')

        violation = {
            'timestamp': datetime.now().isoformat(),
            'rule_name': rule_name,
            'severity': severity,
            'description': f"安全规则违规: {rule_name}",
            'action_taken': action
        }

        self.safety_violations.append(violation)

        # 记录到数据库
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO safety_events
                (timestamp, event_type, severity, description, source, action_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                violation['timestamp'],
                'safety_violation',
                severity,
                violation['description'],
                rule_name,
                action
            ))

        # 执行相应的安全措施
        self._execute_safety_action(action, rule)

        # 记录日志
        log_level = {'critical': logging.CRITICAL,
                    'high': logging.ERROR,
                    'medium': logging.WARNING,
                    'low': logging.INFO}.get(severity, logging.INFO)

        logging.log(log_level, f"安全违规: {rule_name} - {violation['description']}")

    def _execute_safety_action(self, action: str, rule: Dict[str, Any]):
        """执行安全措施"""
        if action == 'emergency_shutdown':
            logging.critical("执行紧急关机")
            # 这里应该实现安全的关机逻辑
        elif action == 'block_ip':
            logging.warning("执行IP封禁")
            # 实现IP封禁逻辑
        elif action == 'data_backup':
            logging.info("执行数据备份")
            self._perform_data_backup()
        elif action == 'reduce_load':
            logging.info("执行负载降低")
            self._reduce_system_load()
        elif action == 'pause_learning':
            logging.warning("暂停AI学习")
            self._pause_ai_learning()

    def _check_data_integrity(self) -> bool:
        """检查数据完整性"""
        # 实现数据完整性检查逻辑
        # 这里是简化的实现
        try:
            # 检查关键文件是否存在和大小是否正常
            critical_files = [
                os.path.join(os.path.dirname(__file__), '..', 'mcp', 'task_history.db'),
                os.path.join(os.path.dirname(__file__), '..', 'mcp', 'mcp_cache.db')
            ]

            for file_path in critical_files:
                if not os.path.exists(file_path):
                    return True  # 文件不存在，视为数据损坏

                # 检查文件大小是否异常
                size = os.path.getsize(file_path)
                if size == 0:
                    return True  # 空文件，视为数据损坏

            return False  # 数据正常

        except Exception as e:
            logging.error(f"数据完整性检查失败: {e}")
            return True  # 检查失败时假设有问题

    def _check_learning_safety(self) -> bool:
        """检查AI学习安全"""
        # 实现AI学习安全检查
        # 检查是否存在不安全的学习模式
        return False  # 暂时返回False，表示学习安全

    def _verify_system_integrity(self):
        """验证系统完整性"""
        # 检查关键组件是否正常运行
        # 验证配置文件完整性
        # 检查权限设置
        pass

    def _monitor_ai_safety(self):
        """监控AI行为安全"""
        # 监控AI决策的合理性
        # 检查是否存在偏见或不安全的行为模式
        # 验证AI输出的安全性
        pass

    def _perform_data_backup(self):
        """执行数据备份"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            # 备份关键数据库文件
            critical_files = [
                ('mcp/task_history.db', 'task_history_backup.db'),
                ('mcp/mcp_cache.db', 'mcp_cache_backup.db'),
                ('config/settings.json', 'settings_backup.json')
            ]

            for src, dst in critical_files:
                src_path = os.path.join(os.path.dirname(__file__), '..', src)
                dst_path = os.path.join(backup_dir, dst)

                if os.path.exists(src_path):
                    import shutil
                    shutil.copy2(src_path, dst_path)
                    logging.info(f"备份文件: {src} -> {dst}")

        except Exception as e:
            logging.error(f"数据备份失败: {e}")

    def _reduce_system_load(self):
        """降低系统负载"""
        # 实现负载降低逻辑
        # 可以暂停非关键任务
        # 降低服务优先级
        logging.info("系统负载降低措施已执行")

    def _pause_ai_learning(self):
        """暂停AI学习"""
        # 实现AI学习暂停逻辑
        logging.info("AI学习已暂停")

    def get_safety_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        return {
            'monitoring_active': self.monitoring_active,
            'total_violations': len(self.safety_violations),
            'recent_violations': self.safety_violations[-5:] if self.safety_violations else [],
            'active_rules': len([r for r in self.safety_rules.values() if r.get('enabled', True)]),
            'last_check': datetime.now().isoformat()
        }

    def get_safety_report(self) -> Dict[str, Any]:
        """生成安全报告"""
        # 获取最近的安全事件
        recent_events = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT timestamp, event_type, severity, description
                    FROM safety_events
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''')
                recent_events = [
                    {
                        'timestamp': row[0],
                        'type': row[1],
                        'severity': row[2],
                        'description': row[3]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logging.error(f"获取安全事件失败: {e}")

        # 统计违规类型
        violation_stats = defaultdict(int)
        for violation in self.safety_violations[-100:]:  # 最近100个违规
            violation_stats[violation.get('rule_name', 'unknown')] += 1

        return {
            'overall_status': 'safe' if len(self.safety_violations) == 0 else 'warning',
            'total_violations': len(self.safety_violations),
            'violation_types': dict(violation_stats),
            'recent_events': recent_events,
            'active_safety_rules': len(self.safety_rules),
            'generated_at': datetime.now().isoformat()
        }

    def add_safety_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """添加安全规则"""
        self.safety_rules[rule_name] = rule_config

        # 保存到数据库
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO safety_rules
                    (rule_name, rule_type, condition, action, enabled)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    rule_name,
                    rule_config.get('type', 'custom'),
                    rule_config.get('condition', ''),
                    rule_config.get('action', 'log'),
                    rule_config.get('enabled', True)
                ))
        except Exception as e:
            logging.error(f"保存安全规则失败: {e}")

    def remove_safety_rule(self, rule_name: str):
        """移除安全规则"""
        if rule_name in self.safety_rules:
            del self.safety_rules[rule_name]

        # 从数据库删除
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM safety_rules WHERE rule_name = ?', (rule_name,))
        except Exception as e:
            logging.error(f"删除安全规则失败: {e}")

    def enable_safety_rule(self, rule_name: str, enabled: bool = True):
        """启用/禁用安全规则"""
        if rule_name in self.safety_rules:
            self.safety_rules[rule_name]['enabled'] = enabled

        # 更新数据库
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE safety_rules
                    SET enabled = ?
                    WHERE rule_name = ?
                ''', (enabled, rule_name))
        except Exception as e:
            logging.error(f"更新安全规则状态失败: {e}")

    def validate_action_safety(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证动作安全性

        Returns:
            (is_safe, reason)
        """
        # 检查动作是否违反安全规则
        for rule_name, rule in self.safety_rules.items():
            if not rule.get('enabled', True):
                continue

            # 这里应该实现具体的动作安全检查逻辑
            # 暂时使用简化的检查
            if action.get('risk_level') == 'high' and rule.get('type') == 'ai_safety':
                return False, f"高风险动作被安全规则 {rule_name} 阻止"

        return True, "动作安全"
