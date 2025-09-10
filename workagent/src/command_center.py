"""
参谋中心 - Command Center for Multi-Model Coordination
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import sqlite3
import queue

class CommandCenter:
    """参谋中心 - 多模型协调与智能决策"""

    def __init__(self):
        self.models = {}  # 可用模型
        self.tasks = queue.Queue()  # 任务队列
        self.active_tasks = {}  # 活跃任务
        self.task_history = []  # 任务历史
        self.performance_metrics = {}  # 性能指标
        self.learning_engine = None  # 学习引擎
        self.decision_maker = None  # 决策制定器
        self.coordination_active = False
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'mcp', 'command_center.db')
        self.init_database()

    def init_database(self):
        """初始化参谋中心数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS task_coordination (
                    id INTEGER PRIMARY KEY,
                    task_id TEXT UNIQUE,
                    timestamp TIMESTAMP,
                    task_type TEXT,
                    assigned_model TEXT,
                    status TEXT,
                    result TEXT,
                    coordination_reasoning TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY,
                    model_name TEXT,
                    timestamp TIMESTAMP,
                    task_type TEXT,
                    success BOOLEAN,
                    response_time REAL,
                    quality_score REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS coordination_decisions (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    decision_type TEXT,
                    context TEXT,
                    chosen_strategy TEXT,
                    expected_outcome TEXT,
                    actual_outcome TEXT
                )
            ''')

    def set_learning_engine(self, learning_engine):
        """设置学习引擎"""
        self.learning_engine = learning_engine

    def set_decision_maker(self, decision_maker):
        """设置决策制定器"""
        self.decision_maker = decision_maker

    def register_model(self, model_name: str, model_info: Dict[str, Any]):
        """注册模型"""
        self.models[model_name] = {
            'info': model_info,
            'status': 'available',
            'performance_history': [],
            'specializations': model_info.get('capabilities', []),
            'last_used': None,
            'usage_count': 0
        }
        logging.info(f"模型已注册: {model_name}")

    def start_coordination(self):
        """启动协调服务"""
        if not self.coordination_active:
            self.coordination_active = True
            coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
            coordination_thread.start()
            logging.info("参谋中心协调服务已启动")

    def stop_coordination(self):
        """停止协调服务"""
        self.coordination_active = False
        logging.info("参谋中心协调服务已停止")

    def _coordination_loop(self):
        """协调主循环"""
        while self.coordination_active:
            try:
                # 处理任务队列
                self._process_task_queue()

                # 更新模型状态
                self._update_model_status()

                # 优化模型分配
                self._optimize_model_allocation()

                # 学习和改进
                self._learn_from_experience()

                time.sleep(10)  # 每10秒协调一次

            except Exception as e:
                logging.error(f"协调循环出错: {e}")
                time.sleep(30)

    def submit_task(self, task: Dict[str, Any]) -> str:
        """提交任务到参谋中心"""
        task_id = f"task_{int(time.time() * 1000)}_{hash(str(task)) % 10000}"
        task_entry = {
            'id': task_id,
            'task': task,
            'submitted_at': datetime.now().isoformat(),
            'status': 'queued',
            'assigned_model': None,
            'result': None
        }

        self.tasks.put(task_entry)
        logging.info(f"任务已提交: {task_id}")
        return task_id

    def _process_task_queue(self):
        """处理任务队列"""
        while not self.tasks.empty() and len(self.active_tasks) < 10:  # 最多同时处理10个任务
            try:
                task_entry = self.tasks.get_nowait()

                # 智能分配模型
                assigned_model = self._intelligent_model_assignment(task_entry['task'])

                if assigned_model:
                    task_entry['assigned_model'] = assigned_model
                    task_entry['status'] = 'processing'
                    self.active_tasks[task_entry['id']] = task_entry

                    # 异步执行任务
                    execution_thread = threading.Thread(
                        target=self._execute_task,
                        args=(task_entry,),
                        daemon=True
                    )
                    execution_thread.start()
                else:
                    # 没有合适的模型，重新放回队列
                    task_entry['status'] = 'retry'
                    self.tasks.put(task_entry)

            except queue.Empty:
                break

    def _intelligent_model_assignment(self, task: Dict[str, Any]) -> Optional[str]:
        """智能模型分配"""
        task_type = self._analyze_task_type(task)
        task_requirements = self._analyze_task_requirements(task)

        # 获取候选模型
        candidates = self._get_candidate_models(task_type, task_requirements)

        if not candidates:
            return None

        # 使用决策制定器选择最佳模型
        if self.decision_maker:
            context = {
                'task_type': task_type,
                'requirements': task_requirements,
                'available_models': candidates,
                'current_load': self._get_current_system_load()
            }

            options = [
                {
                    'model': model_name,
                    'estimated_performance': self._estimate_model_performance(model_name, task_type),
                    'current_load': self.models[model_name].get('current_load', 0),
                    'specialization_match': self._calculate_specialization_match(model_name, task_requirements)
                }
                for model_name in candidates
            ]

            best_option, confidence = self.decision_maker.make_decision(context, options)
            return best_option.get('model') if best_option else None
        else:
            # 简单选择：选择使用频率最低的模型
            return min(candidates, key=lambda m: self.models[m]['usage_count'])

    def _analyze_task_type(self, task: Dict[str, Any]) -> str:
        """分析任务类型"""
        task_description = task.get('task', '').lower()

        if 'code' in task_description or 'program' in task_description:
            return 'coding'
        elif 'analyze' in task_description or 'analysis' in task_description:
            return 'analysis'
        elif 'search' in task_description or 'query' in task_description:
            return 'search'
        elif 'generate' in task_description or 'create' in task_description:
            return 'generation'
        else:
            return 'general'

    def _analyze_task_requirements(self, task: Dict[str, Any]) -> List[str]:
        """分析任务需求"""
        requirements = []
        task_description = task.get('task', '').lower()

        # 基于关键词识别需求
        if 'fast' in task_description or 'quick' in task_description:
            requirements.append('speed')
        if 'accurate' in task_description or 'precise' in task_description:
            requirements.append('accuracy')
        if 'creative' in task_description or 'innovative' in task_description:
            requirements.append('creativity')
        if 'complex' in task_description or 'detailed' in task_description:
            requirements.append('complexity_handling')

        return requirements

    def _get_candidate_models(self, task_type: str, requirements: List[str]) -> List[str]:
        """获取候选模型"""
        candidates = []

        for model_name, model_data in self.models.items():
            if model_data['status'] != 'available':
                continue

            # 检查模型是否支持任务类型
            capabilities = model_data['info'].get('capabilities', [])
            if task_type in capabilities or 'general' in capabilities:
                candidates.append(model_name)

        return candidates

    def _estimate_model_performance(self, model_name: str, task_type: str) -> float:
        """估算模型性能"""
        model_data = self.models[model_name]
        performance_history = model_data.get('performance_history', [])

        if not performance_history:
            return 0.5  # 默认性能

        # 计算该模型在该任务类型上的平均性能
        relevant_performances = [
            p['quality_score'] for p in performance_history
            if p.get('task_type') == task_type
        ]

        if relevant_performances:
            return sum(relevant_performances) / len(relevant_performances)
        else:
            # 使用总体平均性能
            return sum(p['quality_score'] for p in performance_history) / len(performance_history)

    def _calculate_specialization_match(self, model_name: str, requirements: List[str]) -> float:
        """计算专业化匹配度"""
        model_data = self.models[model_name]
        specializations = model_data.get('specializations', [])

        matches = 0
        for req in requirements:
            if req in specializations:
                matches += 1

        return matches / len(requirements) if requirements else 0.5

    def _get_current_system_load(self) -> float:
        """获取当前系统负载"""
        active_count = len(self.active_tasks)
        total_models = len(self.models)
        available_models = sum(1 for m in self.models.values() if m['status'] == 'available')

        # 简单负载计算
        return active_count / max(available_models, 1)

    def _execute_task(self, task_entry: Dict[str, Any]):
        """执行任务"""
        try:
            task = task_entry['task']
            assigned_model = task_entry['assigned_model']

            # 模拟任务执行
            start_time = time.time()
            result = self._simulate_task_execution(task, assigned_model)
            execution_time = time.time() - start_time

            # 更新任务状态
            task_entry['status'] = 'completed'
            task_entry['result'] = result
            task_entry['execution_time'] = execution_time
            task_entry['completed_at'] = datetime.now().isoformat()

            # 记录性能数据
            self._record_task_performance(task_entry, result, execution_time)

            # 通知学习引擎
            if self.learning_engine:
                self.learning_engine.record_experience(
                    task_type=self._analyze_task_type(task),
                    input_data=task,
                    output_data=result,
                    success=result.get('status') == 'success',
                    duration=execution_time,
                    feedback=result.get('feedback', '')
                )

        except Exception as e:
            logging.error(f"任务执行失败: {e}")
            task_entry['status'] = 'failed'
            task_entry['error'] = str(e)
        finally:
            # 从活跃任务中移除
            if task_entry['id'] in self.active_tasks:
                del self.active_tasks[task_entry['id']]

            # 添加到历史
            self.task_history.append(task_entry)

    def _simulate_task_execution(self, task: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """模拟任务执行"""
        # 这里是简化的任务执行模拟
        # 实际实现应该调用真实的模型API

        time.sleep(1)  # 模拟处理时间

        return {
            'status': 'success',
            'model_used': model_name,
            'result': f"任务 '{task.get('task', '')}' 已由模型 {model_name} 处理完成",
            'confidence': 0.85,
            'feedback': '任务执行顺利'
        }

    def _record_task_performance(self, task_entry: Dict[str, Any], result: Dict[str, Any], execution_time: float):
        """记录任务性能"""
        model_name = task_entry['assigned_model']
        task_type = self._analyze_task_type(task_entry['task'])

        performance_record = {
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'success': result.get('status') == 'success',
            'response_time': execution_time,
            'quality_score': result.get('confidence', 0.5)
        }

        # 更新模型性能历史
        if model_name in self.models:
            self.models[model_name]['performance_history'].append(performance_record)
            self.models[model_name]['usage_count'] += 1
            self.models[model_name]['last_used'] = datetime.now().isoformat()

            # 只保留最近100个性能记录
            if len(self.models[model_name]['performance_history']) > 100:
                self.models[model_name]['performance_history'] = self.models[model_name]['performance_history'][-100:]

        # 保存到数据库
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO model_performance
                (model_name, timestamp, task_type, success, response_time, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                performance_record['model_name'],
                performance_record['timestamp'],
                performance_record['task_type'],
                performance_record['success'],
                performance_record['response_time'],
                performance_record['quality_score']
            ))

    def _update_model_status(self):
        """更新模型状态"""
        for model_name, model_data in self.models.items():
            # 检查模型是否仍然可用
            # 这里可以实现更复杂的健康检查逻辑
            model_data['status'] = 'available'  # 简化实现

    def _optimize_model_allocation(self):
        """优化模型分配"""
        # 分析模型使用模式
        # 调整模型优先级
        # 预测未来需求
        pass

    def _learn_from_experience(self):
        """从经验中学习"""
        if not self.learning_engine:
            return

        # 分析最近的任务执行情况
        recent_tasks = [t for t in self.task_history[-50:]]  # 最近50个任务

        if recent_tasks:
            # 计算整体性能指标
            success_rate = sum(1 for t in recent_tasks if t.get('status') == 'completed') / len(recent_tasks)
            avg_response_time = sum(t.get('execution_time', 0) for t in recent_tasks) / len(recent_tasks)

            # 基于性能调整策略
            if success_rate < 0.8:
                logging.info("检测到成功率偏低，正在调整分配策略")
            if avg_response_time > 5.0:
                logging.info("检测到响应时间偏长，正在优化模型选择")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 检查活跃任务
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]

        # 检查历史任务
        for task in self.task_history:
            if task['id'] == task_id:
                return task

        return None

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'active_models': len([m for m in self.models.values() if m['status'] == 'available']),
            'total_models': len(self.models),
            'queued_tasks': self.tasks.qsize(),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len([t for t in self.task_history if t.get('status') == 'completed']),
            'coordination_active': self.coordination_active,
            'system_load': self._get_current_system_load()
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        model_performance = {}

        for model_name, model_data in self.models.items():
            performances = model_data.get('performance_history', [])
            if performances:
                success_rate = sum(1 for p in performances if p['success']) / len(performances)
                avg_response_time = sum(p['response_time'] for p in performances) / len(performances)
                avg_quality = sum(p['quality_score'] for p in performances) / len(performances)

                model_performance[model_name] = {
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'avg_quality_score': avg_quality,
                    'usage_count': model_data['usage_count']
                }

        return {
            'generated_at': datetime.now().isoformat(),
            'model_performance': model_performance,
            'overall_metrics': self._calculate_overall_metrics(model_performance),
            'recommendations': self._generate_performance_recommendations(model_performance)
        }

    def _calculate_overall_metrics(self, model_performance: Dict[str, Any]) -> Dict[str, Any]:
        """计算整体指标"""
        if not model_performance:
            return {}

        total_tasks = sum(m['usage_count'] for m in model_performance.values())
        weighted_success = sum(m['success_rate'] * m['usage_count'] for m in model_performance.values())
        weighted_response_time = sum(m['avg_response_time'] * m['usage_count'] for m in model_performance.values())

        return {
            'overall_success_rate': weighted_success / total_tasks if total_tasks > 0 else 0,
            'overall_avg_response_time': weighted_response_time / total_tasks if total_tasks > 0 else 0,
            'total_tasks_processed': total_tasks,
            'active_models': len(model_performance)
        }

    def _generate_performance_recommendations(self, model_performance: Dict[str, Any]) -> List[str]:
        """生成性能建议"""
        recommendations = []

        if not model_performance:
            return ["暂无性能数据"]

        # 识别低性能模型
        low_performers = [
            name for name, perf in model_performance.items()
            if perf['success_rate'] < 0.7 or perf['avg_response_time'] > 5.0
        ]

        if low_performers:
            recommendations.append(f"以下模型性能需要优化: {', '.join(low_performers)}")

        # 检查负载均衡
        usage_counts = [perf['usage_count'] for perf in model_performance.values()]
        if usage_counts and max(usage_counts) / (min(usage_counts) or 1) > 3:
            recommendations.append("模型使用不均衡，建议优化任务分配策略")

        return recommendations

    def emergency_shutdown(self):
        """紧急关闭"""
        logging.warning("执行参谋中心紧急关闭")
        self.coordination_active = False

        # 取消所有活跃任务
        for task_id in list(self.active_tasks.keys()):
            task = self.active_tasks[task_id]
            task['status'] = 'cancelled'
            task['cancelled_at'] = datetime.now().isoformat()
            self.task_history.append(task)
            del self.active_tasks[task_id]

        logging.info("参谋中心紧急关闭完成")
