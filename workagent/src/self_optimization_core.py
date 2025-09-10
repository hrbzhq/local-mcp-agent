"""
自主优化系统 - Self-Optimizing AI Ecosystem
实现Agent自主优化、MCP自主优化和参谋中心
"""

import os
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import sqlite3
import inspect

# 导入其他组件
from .learning_engine import LearningEngine
from .decision_maker import DecisionMaker
from .resource_manager import ResourceManager
from .safety_monitor import SafetyMonitor
from .capability_boundary_expander import CapabilityBoundaryExpander
from .mcp_evolution_optimizer import MCPEvolutionOptimizer
import importlib
import sys

class SelfOptimizationCore:
    """自主优化核心系统"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', 'mcp', 'optimization.db')
        self.learning_engine = LearningEngine()
        self.decision_maker = DecisionMaker()
        self.resource_manager = ResourceManager()
        self.safety_monitor = SafetyMonitor()

        # 新增的自主优化组件
        self.capability_expander = CapabilityBoundaryExpander()
        self.mcp_evolution_optimizer = MCPEvolutionOptimizer()

        self.init_database()

    def init_database(self):
        """初始化优化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    component TEXT,
                    action TEXT,
                    result TEXT,
                    metrics TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS capability_inventory (
                    id INTEGER PRIMARY KEY,
                    component TEXT,
                    capability TEXT,
                    proficiency REAL,
                    last_used TIMESTAMP,
                    usage_count INTEGER
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learning_goals (
                    id INTEGER PRIMARY KEY,
                    goal TEXT,
                    priority INTEGER,
                    status TEXT,
                    progress REAL,
                    created TIMESTAMP
                )
            ''')

    def start_autonomous_optimization(self):
        """启动自主优化循环"""
        optimization_thread = threading.Thread(
            target=self._optimization_loop,
            daemon=True
        )
        optimization_thread.start()
        logging.info("自主优化系统已启动")

    def stop_autonomous_optimization(self):
        """停止自主优化循环"""
        # 设置停止标志（需要在优化循环中检查这个标志）
        self.optimization_active = False
        logging.info("正在停止自主优化系统...")

        # 停止子组件
        try:
            if hasattr(self.capability_expander, 'stop_expansion'):
                self.capability_expander.stop_expansion()
        except Exception as e:
            logging.warning(f"停止能力扩展器时出错: {e}")

        try:
            if hasattr(self.mcp_evolution_optimizer, 'stop_evolution'):
                self.mcp_evolution_optimizer.stop_evolution()
        except Exception as e:
            logging.warning(f"停止MCP进化器时出错: {e}")

        logging.info("自主优化系统已停止")

    def start_optimization(self):
        """启动优化（系统集成器接口）"""
        self.start_autonomous_optimization()

    def _optimization_loop(self):
        """优化主循环"""
        self.optimization_active = True
        while self.optimization_active:
            try:
                # 1. 评估当前状态
                system_status = self._assess_system_status()

                # 2. 识别优化机会
                opportunities = self._identify_optimization_opportunities(system_status)

                # 3. 执行能力边界扩展（低频任务）
                if int(time.time()) % 3600 == 0:  # 每小时执行一次
                    self._execute_capability_expansion()

                # 4. 执行MCP进化优化（低频任务）
                if int(time.time()) % 7200 == 0:  # 每2小时执行一次
                    self._execute_mcp_evolution()

                # 5. 制定优化计划
                optimization_plan = self._create_optimization_plan(opportunities)

                # 6. 执行优化
                self._execute_optimization_plan(optimization_plan)

                # 7. 评估优化效果
                self._evaluate_optimization_results()

                # 等待下一轮优化
                time.sleep(300)  # 5分钟检查一次

            except Exception as e:
                logging.error(f"优化循环出错: {e}")
                time.sleep(60)  # 出错后等待1分钟

    def _assess_system_status(self) -> Dict[str, Any]:
        """评估系统当前状态"""
        return {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self._get_performance_metrics(),
            'capability_inventory': self._get_capability_inventory(),
            'resource_usage': self.resource_manager.get_resource_usage(),
            'safety_status': self.safety_monitor.get_safety_status()
        }

    def _identify_optimization_opportunities(self, status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别优化机会"""
        opportunities = []

        # 检查性能瓶颈
        if status['performance_metrics']['response_time'] > 5.0:
            opportunities.append({
                'type': 'performance',
                'component': 'response_optimization',
                'priority': 'high',
                'description': '响应时间过长，需要优化'
            })

        # 检查能力空白
        missing_capabilities = self._identify_missing_capabilities()
        for capability in missing_capabilities:
            opportunities.append({
                'type': 'capability',
                'component': 'agent',
                'priority': 'medium',
                'description': f'缺少能力: {capability}',
                'capability': capability
            })

        # 检查资源使用效率
        if status['resource_usage']['cpu']['percent'] > 80:
            opportunities.append({
                'type': 'resource',
                'component': 'resource_optimization',
                'priority': 'high',
                'description': 'CPU使用率过高，需要优化'
            })

        return opportunities

    def _create_optimization_plan(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """制定优化计划"""
        plan = {
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'estimated_duration': 0,
            'risk_assessment': 'low'
        }

        for opportunity in sorted(opportunities, key=lambda x: self._get_priority_score(x['priority']), reverse=True):
            if len(plan['actions']) >= 3:  # 每次最多执行3个优化动作
                break

            action = self._create_optimization_action(opportunity)
            if action:
                plan['actions'].append(action)
                plan['estimated_duration'] += action.get('estimated_duration', 0)

        return plan

    def _execute_optimization_plan(self, plan: Dict[str, Any]):
        """执行优化计划"""
        for action in plan['actions']:
            try:
                self._execute_action(action)
                self._record_optimization_history(action, 'success')
            except Exception as e:
                logging.error(f"执行优化动作失败: {e}")
                self._record_optimization_history(action, 'failed', str(e))

    def _evaluate_optimization_results(self):
        """评估优化效果"""
        # 比较优化前后的性能指标
        # 更新学习模型
        # 调整未来优化策略
        pass

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            'response_time': 2.5,  # 示例值
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'error_rate': 0.02
        }

    def _get_capability_inventory(self) -> Dict[str, Any]:
        """获取能力清单"""
        return {
            'agent_capabilities': ['text_generation', 'code_generation', 'analysis'],
            'mcp_modules': ['database', 'file_processor', 'web_scraper'],
            'integration_points': ['ollama', 'sqlite', 'flask']
        }

    def _identify_missing_capabilities(self) -> List[str]:
        """识别缺少的能力"""
        # 基于历史任务分析缺少的能力
        return ['image_processing', 'video_analysis', 'advanced_math']

    def _get_priority_score(self, priority: str) -> int:
        """获取优先级分数"""
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        return priority_map.get(priority, 1)

    def _create_optimization_action(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建优化动作"""
        action_type = opportunity['type']

        if action_type == 'performance':
            return {
                'id': f"perf_opt_{int(time.time())}",
                'type': 'performance_optimization',
                'description': opportunity['description'],
                'estimated_duration': 10,
                'risk_level': 'low'
            }
        elif action_type == 'capability':
            return {
                'id': f"cap_acq_{int(time.time())}",
                'type': 'capability_acquisition',
                'description': opportunity['description'],
                'capability': opportunity['capability'],
                'estimated_duration': 30,
                'risk_level': 'medium'
            }
        elif action_type == 'resource':
            return {
                'id': f"res_opt_{int(time.time())}",
                'type': 'resource_optimization',
                'description': opportunity['description'],
                'estimated_duration': 15,
                'risk_level': 'low'
            }

        return None

    def _execute_action(self, action: Dict[str, Any]):
        """执行优化动作"""
        action_type = action['type']

        if action_type == 'performance_optimization':
            self._optimize_performance()
        elif action_type == 'capability_acquisition':
            self._acquire_capability(action['capability'])
        elif action_type == 'resource_optimization':
            self._optimize_resources()

    def _optimize_performance(self):
        """优化性能"""
        # 实现性能优化逻辑
        logging.info("执行性能优化")

    def _acquire_capability(self, capability: str):
        """获取新能力"""
        # 实现能力获取逻辑
        logging.info(f"获取新能力: {capability}")

    def _optimize_resources(self):
        """优化资源使用"""
        # 实现资源优化逻辑
        logging.info("执行资源优化")

    def _record_optimization_history(self, action: Dict[str, Any], result: str, error: str = None):
        """记录优化历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO optimization_history
                (timestamp, component, action, result, metrics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                action.get('type', 'unknown'),
                action.get('description', ''),
                result,
                json.dumps({'error': error} if error else {})
            ))

    def _execute_capability_expansion(self):
        """执行能力边界扩展"""
        try:
            # 确保能力扩展器已启动
            if not hasattr(self.capability_expander, 'expansion_active') or not self.capability_expander.expansion_active:
                self.capability_expander.start_expansion()

            # 执行一次扩展循环
            self.capability_expander._analyze_capability_usage()
            self.capability_expander._identify_skill_gaps()

            expansion_plan = self.capability_expander._create_expansion_plan()
            if expansion_plan:
                self.capability_expander._execute_expansion_plan(expansion_plan)
                logging.info(f"能力边界扩展完成，处理了 {len(expansion_plan)} 个扩展任务")

        except Exception as e:
            logging.error(f"执行能力边界扩展时出错: {e}")

    def _execute_mcp_evolution(self):
        """执行MCP进化优化"""
        try:
            # 确保MCP进化器已启动
            if not hasattr(self.mcp_evolution_optimizer, 'evolution_active') or not self.mcp_evolution_optimizer.evolution_active:
                self.mcp_evolution_optimizer.start_evolution()

            # 执行一次进化循环
            self.mcp_evolution_optimizer._analyze_module_usage()
            self.mcp_evolution_optimizer._assess_module_quality()

            new_requirements = self.mcp_evolution_optimizer._discover_new_requirements()
            if new_requirements:
                evolution_plan = self.mcp_evolution_optimizer._create_evolution_plan(new_requirements)
                if evolution_plan:
                    self.mcp_evolution_optimizer._execute_evolution_plan(evolution_plan)
                    logging.info(f"MCP进化优化完成，发现 {len(new_requirements)} 个需求，执行 {len(evolution_plan)} 个进化任务")

        except Exception as e:
            logging.error(f"执行MCP进化优化时出错: {e}")

    def get_capability_expansion_status(self) -> Dict[str, Any]:
        """获取能力扩展状态"""
        if hasattr(self.capability_expander, 'get_expansion_status'):
            return self.capability_expander.get_expansion_status()
        return {'error': 'Capability expander not available'}

    def get_mcp_evolution_status(self) -> Dict[str, Any]:
        """获取MCP进化状态"""
        if hasattr(self.mcp_evolution_optimizer, 'get_evolution_status'):
            return self.mcp_evolution_optimizer.get_evolution_status()
        return {'error': 'MCP evolution optimizer not available'}
