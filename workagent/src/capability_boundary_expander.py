"""
能力边界扩展器 - Capability Boundary Expander
实现Agent自主优化，基于使用频率和需求分析主动学习新技能
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
import sqlite3
import importlib
import inspect

class CapabilityBoundaryExpander:
    """能力边界扩展器"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', 'mcp', 'capability_expansion.db')
        self.capability_inventory = {}  # 能力清单
        self.usage_patterns = defaultdict(int)  # 使用模式统计
        self.skill_gaps = []  # 技能空白
        self.expansion_active = False
        self.expansion_thread = None
        self.init_database()

    def init_database(self):
        """初始化能力扩展数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS capability_usage (
                    id INTEGER PRIMARY KEY,
                    capability TEXT,
                    timestamp TIMESTAMP,
                    usage_count INTEGER,
                    success_rate REAL,
                    context TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS skill_gaps (
                    id INTEGER PRIMARY KEY,
                    gap_type TEXT,
                    description TEXT,
                    priority INTEGER,
                    detected_at TIMESTAMP,
                    addressed BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS expansion_history (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    capability TEXT,
                    expansion_type TEXT,
                    result TEXT,
                    metrics TEXT
                )
            ''')

    def start_expansion(self):
        """启动能力边界扩展"""
        if not self.expansion_active:
            self.expansion_active = True
            self.expansion_thread = threading.Thread(target=self._expansion_loop, daemon=True)
            self.expansion_thread.start()
            logging.info("能力边界扩展已启动")

    def stop_expansion(self):
        """停止能力边界扩展"""
        self.expansion_active = False
        logging.info("能力边界扩展已停止")

    def _expansion_loop(self):
        """扩展主循环"""
        while self.expansion_active:
            try:
                # 1. 分析当前能力使用情况
                self._analyze_capability_usage()

                # 2. 识别技能空白
                self._identify_skill_gaps()

                # 3. 制定扩展计划
                expansion_plan = self._create_expansion_plan()

                # 4. 执行扩展
                self._execute_expansion_plan(expansion_plan)

                # 等待下一轮扩展（每小时检查一次）
                time.sleep(3600)

            except Exception as e:
                logging.error(f"能力扩展循环出错: {e}")
                time.sleep(300)  # 出错后等待5分钟

    def _analyze_capability_usage(self):
        """分析能力使用情况"""
        # 获取最近7天的使用数据
        cutoff_time = datetime.now() - timedelta(days=7)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT capability, COUNT(*) as usage_count,
                       AVG(success_rate) as avg_success_rate
                FROM capability_usage
                WHERE timestamp > ?
                GROUP BY capability
                ORDER BY usage_count DESC
            ''', (cutoff_time.isoformat(),))

            self.capability_inventory = {}
            for row in cursor:
                capability, usage_count, success_rate = row
                self.capability_inventory[capability] = {
                    'usage_count': usage_count,
                    'success_rate': success_rate or 0,
                    'last_updated': datetime.now().isoformat()
                }

        logging.info(f"分析了 {len(self.capability_inventory)} 个能力的近期使用情况")

    def _identify_skill_gaps(self):
        """识别技能空白"""
        self.skill_gaps = []

        # 分析高频任务但成功率低的能力
        for capability, stats in self.capability_inventory.items():
            if stats['usage_count'] > 10 and stats['success_rate'] < 0.7:
                self.skill_gaps.append({
                    'type': 'improvement',
                    'capability': capability,
                    'description': f"{capability} 使用频繁但成功率低 ({stats['success_rate']:.2f})",
                    'priority': 3 if stats['usage_count'] > 50 else 2,
                    'usage_count': stats['usage_count']
                })

        # 分析新兴需求（基于任务模式）
        emerging_patterns = self._detect_emerging_patterns()
        for pattern in emerging_patterns:
            if pattern not in self.capability_inventory:
                self.skill_gaps.append({
                    'type': 'new_capability',
                    'capability': pattern,
                    'description': f"检测到新兴需求模式: {pattern}",
                    'priority': 2,
                    'usage_count': 0
                })

        # 按优先级和使用频率排序
        self.skill_gaps.sort(key=lambda x: (x['priority'], x['usage_count']), reverse=True)

        logging.info(f"识别出 {len(self.skill_gaps)} 个技能空白")

    def _detect_emerging_patterns(self) -> List[str]:
        """检测新兴模式"""
        # 分析任务历史，识别频繁出现的模式
        patterns = []

        # 这里可以集成更复杂的模式识别算法
        # 目前使用简单的关键词分析
        common_patterns = [
            'data_analysis', 'image_processing', 'text_summarization',
            'code_generation', 'api_integration', 'database_query',
            'file_processing', 'web_scraping', 'automation'
        ]

        return common_patterns

    def _create_expansion_plan(self) -> List[Dict[str, Any]]:
        """制定扩展计划"""
        plan = []

        # 只处理高优先级的技能空白
        high_priority_gaps = [gap for gap in self.skill_gaps if gap['priority'] >= 2]

        for gap in high_priority_gaps[:3]:  # 每次最多处理3个扩展任务
            if gap['type'] == 'improvement':
                plan.append({
                    'type': 'capability_improvement',
                    'capability': gap['capability'],
                    'description': f"改进 {gap['capability']} 的成功率",
                    'estimated_effort': 2,  # 2小时
                    'priority': gap['priority']
                })
            elif gap['type'] == 'new_capability':
                plan.append({
                    'type': 'capability_acquisition',
                    'capability': gap['capability'],
                    'description': f"学习新能力: {gap['capability']}",
                    'estimated_effort': 4,  # 4小时
                    'priority': gap['priority']
                })

        return plan

    def _execute_expansion_plan(self, plan: List[Dict[str, Any]]):
        """执行扩展计划"""
        for action in plan:
            try:
                if action['type'] == 'capability_improvement':
                    self._improve_capability(action['capability'])
                elif action['type'] == 'capability_acquisition':
                    self._acquire_capability(action['capability'])

                # 记录扩展历史
                self._record_expansion_history(action, 'success')

            except Exception as e:
                logging.error(f"执行扩展动作失败: {e}")
                self._record_expansion_history(action, 'failed', str(e))

    def _improve_capability(self, capability: str):
        """改进现有能力"""
        logging.info(f"开始改进能力: {capability}")

        # 这里可以实现具体的改进逻辑
        # 例如：调整参数、更新算法、增加训练数据等

        # 模拟改进过程
        time.sleep(1)  # 模拟处理时间

        logging.info(f"能力 {capability} 改进完成")

    def _acquire_capability(self, capability: str):
        """获取新能力"""
        logging.info(f"开始学习新能力: {capability}")

        # 这里可以实现新能力的学习逻辑
        # 例如：从模板生成代码、配置参数、测试验证等

        # 模拟学习过程
        time.sleep(2)  # 模拟处理时间

        logging.info(f"新能力 {capability} 学习完成")

    def _record_expansion_history(self, action: Dict[str, Any], result: str, error: str = None):
        """记录扩展历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO expansion_history
                (timestamp, capability, expansion_type, result, metrics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                action.get('capability', ''),
                action.get('type', ''),
                result,
                json.dumps({'error': error} if error else {})
            ))

    def record_capability_usage(self, capability: str, success: bool, context: str = None):
        """记录能力使用情况"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO capability_usage
                (capability, timestamp, usage_count, success_rate, context)
                VALUES (?, ?, 1, ?, ?)
            ''', (
                capability,
                datetime.now().isoformat(),
                1.0 if success else 0.0,
                context or ''
            ))

    def get_expansion_status(self) -> Dict[str, Any]:
        """获取扩展状态"""
        return {
            'active': self.expansion_active,
            'capability_count': len(self.capability_inventory),
            'skill_gaps_count': len(self.skill_gaps),
            'high_priority_gaps': len([g for g in self.skill_gaps if g['priority'] >= 2])
        }
