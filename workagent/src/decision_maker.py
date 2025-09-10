"""
决策制定器 - Decision Maker for Autonomous Optimization
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import sqlite3
import os


class DecisionMaker:
    """决策制定器"""

    def __init__(self):
        self.decision_history = []
        self.decision_patterns = defaultdict(int)
        self.confidence_threshold = 0.7
        self.risk_tolerance = 0.3
        self.learning_engine = None  # 学习引擎引用
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'mcp', 'decisions.db')
        self.init_database()

    def set_learning_engine(self, learning_engine):
        """设置学习引擎"""
        self.learning_engine = learning_engine
        logging.info("学习引擎已连接到决策制定器")

    def init_database(self):
        """初始化决策数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    context TEXT,
                    options TEXT,
                    chosen_option TEXT,
                    confidence REAL,
                    outcome TEXT,
                    feedback TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS decision_rules (
                    id INTEGER PRIMARY KEY,
                    condition TEXT,
                    action TEXT,
                    confidence REAL,
                    usage_count INTEGER,
                    last_used TIMESTAMP
                )
            ''')

    def make_decision(self, context: Dict[str, Any], options: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """
        制定决策

        Args:
            context: 决策上下文
            options: 可选方案列表

        Returns:
            (选择的方案, 置信度)
        """
        if not options:
            return None, 0.0

        if len(options) == 1:
            return options[0], 0.8  # 只有一个选项时默认中等置信度

        # 评估每个选项
        option_scores = []
        for option in options:
            score, confidence = self._evaluate_option(option, context)
            option_scores.append((option, score, confidence))

        # 选择最佳选项
        best_option, best_score, confidence = max(option_scores, key=lambda x: x[1])

        # 记录决策
        self._record_decision(context, options, best_option, confidence)

        return best_option, confidence

    def _evaluate_option(self, option: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float]:
        """
        评估选项

        Returns:
            (分数, 置信度)
        """
        score = 0.0
        confidence_factors = []

        # 基于历史表现评估
        historical_score, historical_confidence = self._evaluate_historical_performance(option, context)
        score += historical_score * 0.4
        confidence_factors.append(historical_confidence)

        # 基于风险评估
        risk_score, risk_confidence = self._evaluate_risk(option, context)
        score += risk_score * 0.3
        confidence_factors.append(risk_confidence)

        # 基于资源消耗评估
        resource_score, resource_confidence = self._evaluate_resource_impact(option, context)
        score += resource_score * 0.2
        confidence_factors.append(resource_confidence)

        # 基于创新性评估
        innovation_score, innovation_confidence = self._evaluate_innovation(option, context)
        score += innovation_score * 0.1
        confidence_factors.append(innovation_confidence)

        # 计算综合置信度
        overall_confidence = min(confidence_factors) if confidence_factors else 0.5

        return score, overall_confidence

    def _evaluate_historical_performance(self, option: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float]:
        """基于历史表现评估"""
        option_type = option.get('type', 'unknown')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                       COUNT(*) as total_decisions
                FROM decisions
                WHERE chosen_option LIKE ?
            ''', (f'%{option_type}%',))

            row = cursor.fetchone()
            if row and row[1] > 0:
                success_rate = row[0] or 0.5
                confidence = min(1.0, row[1] / 10)  # 基于样本数量计算置信度
                return success_rate * 100, confidence
            else:
                return 50, 0.3  # 默认分数和置信度

    def _evaluate_risk(self, option: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float]:
        """评估风险"""
        risk_level = option.get('risk_level', 'medium')
        risk_scores = {'low': 80, 'medium': 60, 'high': 30}

        base_score = risk_scores.get(risk_level, 50)

        # 根据当前系统状态调整风险评估
        system_load = context.get('system_load', 0.5)
        if system_load > 0.8 and risk_level == 'high':
            base_score -= 20  # 高负载时降低高风险选项分数

        confidence = 0.8 if risk_level in risk_scores else 0.5

        return base_score, confidence

    def _evaluate_resource_impact(self, option: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float]:
        """评估资源影响"""
        resource_usage = option.get('estimated_resources', {})

        cpu_usage = resource_usage.get('cpu', 0)
        memory_usage = resource_usage.get('memory', 0)

        # 计算资源效率分数
        efficiency_score = 100 - (cpu_usage + memory_usage) / 2

        # 考虑当前资源可用性
        available_cpu = context.get('available_cpu', 100)
        available_memory = context.get('available_memory', 100)

        if cpu_usage > available_cpu or memory_usage > available_memory:
            efficiency_score -= 30  # 资源不足时降低分数

        confidence = 0.7

        return max(0, efficiency_score), confidence

    def _evaluate_innovation(self, option: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float]:
        """评估创新性"""
        # 偏好创新选项，但要考虑稳定性
        is_innovative = option.get('is_innovative', False)
        is_experimental = option.get('is_experimental', False)

        if is_innovative and not is_experimental:
            score = 80
        elif is_experimental:
            score = 60
        else:
            score = 70

        confidence = 0.6  # 创新性评估的置信度相对较低

        return score, confidence

    def _record_decision(
        self,
        context: Dict[str, Any],
        options: List[Dict[str, Any]],
        chosen_option: Dict[str, Any],
        confidence: float,
    ):
        """记录决策"""
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'context': json.dumps(context),
            'options': json.dumps(options),
            'chosen_option': json.dumps(chosen_option),
            'confidence': confidence,
            'outcome': 'pending',  # 初始状态为待定
            'feedback': ''
        }

        self.decision_history.append(decision_record)

        # 持久化存储
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''
                INSERT INTO decisions
                (timestamp, context, options, chosen_option, confidence, outcome, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                    decision_record['timestamp'],
                    decision_record['context'],
                    decision_record['options'],
                    decision_record['chosen_option'],
                    decision_record['confidence'],
                    decision_record['outcome'],
                    decision_record['feedback'],
                ))

    def update_decision_outcome(self, decision_id: int, outcome: str, feedback: str = ""):
        """更新决策结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE decisions
                SET outcome = ?, feedback = ?
                WHERE id = ?
            ''', (outcome, feedback, decision_id))

        # 更新决策模式
        self.decision_patterns[f"outcome_{outcome}"] += 1

    def learn_from_feedback(self, feedback_data: Dict[str, Any]):
        """从反馈中学习"""
        # 分析反馈模式
        # 更新决策规则
        # 调整评估权重
        pass

    def get_decision_insights(self) -> Dict[str, Any]:
        """获取决策洞察"""
        insights = {
            'total_decisions': len(self.decision_history),
            'success_rate': self._calculate_success_rate(),
            'common_patterns': dict(self.decision_patterns),
            'risk_distribution': self._analyze_risk_distribution(),
            'learning_progress': self._analyze_learning_progress()
        }

        return insights

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successful
                FROM decisions
                WHERE outcome != 'pending'
            ''')

            row = cursor.fetchone()
            if row and row[0] > 0:
                return row[1] / row[0]
            else:
                return 0.0

    def _analyze_risk_distribution(self) -> Dict[str, int]:
        """分析风险分布"""
        risk_counts = defaultdict(int)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT chosen_option
                FROM decisions
            ''')

            for row in cursor:
                try:
                    option = json.loads(row[0])
                    risk_level = option.get('risk_level', 'unknown')
                    risk_counts[risk_level] += 1
                except Exception as e:
                    # 解析单条记录失败，计为 unknown 并记录简短信息
                    risk_counts['unknown'] += 1
                    print(f"Warning: failed to parse decision option: {e}")

        return dict(risk_counts)

    def _analyze_learning_progress(self) -> Dict[str, Any]:
        """分析学习进度"""
        # 计算决策质量随时间的变化
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DATE(timestamp) as date,
                       AVG(confidence) as avg_confidence,
                       SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
                FROM decisions
                WHERE outcome != 'pending'
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''')

            progress_data = []
            for row in cursor:
                progress_data.append({
                    'date': row[0],
                    'avg_confidence': row[1],
                    'success_rate': row[2]
                })

        return {
            'data_points': len(progress_data),
            'trend': self._calculate_trend(progress_data),
            'recent_performance': progress_data[-5:] if len(progress_data) >= 5 else progress_data
        }

    def _calculate_trend(self, data: List[Dict[str, Any]]) -> str:
        """计算趋势"""
        if len(data) < 2:
            return 'insufficient_data'

        # 计算成功率的趋势
        success_rates = [item['success_rate'] for item in data[-10:]]  # 最近10个数据点

        if len(success_rates) >= 2:
            recent_slice = success_rates[-3:] if len(success_rates) >= 3 else success_rates[-1:]
            earlier_slice = success_rates[:-3] if len(success_rates) > 3 else success_rates[:1]

            recent_avg = sum(recent_slice) / len(recent_slice)
            earlier_avg = sum(earlier_slice) / len(earlier_slice)

            if recent_avg > earlier_avg + 0.05:
                return 'improving'
            elif recent_avg < earlier_avg - 0.05:
                return 'declining'
            else:
                return 'stable'

        return 'stable'
