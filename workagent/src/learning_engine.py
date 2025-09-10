"""
学习引擎 - Learning Engine for Autonomous Optimization
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import sqlite3
import os

class LearningEngine:
    """学习引擎"""

    def __init__(self):
        self.knowledge_base = {}
        self.experience_memory = []
        self.learning_patterns = defaultdict(int)
        self.skill_proficiency = defaultdict(float)
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'mcp', 'learning.db')
        self.init_database()

    def init_database(self):
        """初始化学习数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    task_type TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    success BOOLEAN,
                    duration REAL,
                    feedback TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT UNIQUE,
                    proficiency REAL,
                    usage_count INTEGER,
                    last_used TIMESTAMP,
                    category TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    confidence REAL,
                    occurrences INTEGER,
                    last_seen TIMESTAMP
                )
            ''')

    def record_experience(self, task_type: str, input_data: Any, output_data: Any,
                         success: bool, duration: float, feedback: str = ""):
        """记录经验"""
        experience = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'input_data': json.dumps(input_data) if not isinstance(input_data, str) else input_data,
            'output_data': json.dumps(output_data) if not isinstance(output_data, str) else output_data,
            'success': success,
            'duration': duration,
            'feedback': feedback
        }

        self.experience_memory.append(experience)

        # 持久化存储
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO experiences
                (timestamp, task_type, input_data, output_data, success, duration, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                experience['timestamp'],
                experience['task_type'],
                experience['input_data'],
                experience['output_data'],
                experience['success'],
                experience['duration'],
                experience['feedback']
            ))

        # 更新技能熟练度
        self._update_skill_proficiency(task_type, success, duration)

        # 识别模式
        self._identify_patterns(experience)

    def _update_skill_proficiency(self, task_type: str, success: bool, duration: float):
        """更新技能熟练度"""
        current_proficiency = self.skill_proficiency[task_type]

        # 基于成功率和效率调整熟练度
        success_bonus = 0.1 if success else -0.05
        efficiency_bonus = max(-0.05, min(0.05, (10 - duration) / 100))  # 基于执行时间

        new_proficiency = min(1.0, max(0.0, current_proficiency + success_bonus + efficiency_bonus))
        self.skill_proficiency[task_type] = new_proficiency

        # 更新数据库
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO skills
                (skill_name, proficiency, usage_count, last_used, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                task_type,
                new_proficiency,
                self.learning_patterns[task_type] + 1,
                datetime.now().isoformat(),
                self._categorize_skill(task_type)
            ))

    def _identify_patterns(self, experience: Dict[str, Any]):
        """识别模式"""
        task_type = experience['task_type']
        self.learning_patterns[task_type] += 1

        # 识别时间模式
        hour = datetime.fromisoformat(experience['timestamp']).hour
        time_pattern = f"time_{hour//4 * 4:02d}-{hour//4 * 4 + 4:02d}"
        self.learning_patterns[time_pattern] += 1

        # 识别成功模式
        if experience['success']:
            success_pattern = f"success_{task_type}"
            self.learning_patterns[success_pattern] += 1

    def _categorize_skill(self, skill_name: str) -> str:
        """对技能进行分类"""
        if 'code' in skill_name.lower() or 'program' in skill_name.lower():
            return 'programming'
        elif 'analysis' in skill_name.lower() or 'analyze' in skill_name.lower():
            return 'analysis'
        elif 'search' in skill_name.lower() or 'query' in skill_name.lower():
            return 'search'
        elif 'generate' in skill_name.lower() or 'create' in skill_name.lower():
            return 'generation'
        else:
            return 'general'

    def predict_task_success(self, task_type: str, context: Dict[str, Any]) -> float:
        """预测任务成功率"""
        base_success_rate = self._get_historical_success_rate(task_type)

        # 考虑上下文因素
        context_multiplier = self._calculate_context_multiplier(context)

        # 考虑时间因素
        time_multiplier = self._calculate_time_multiplier()

        # 考虑技能熟练度
        proficiency_multiplier = self.skill_proficiency.get(task_type, 0.5)

        predicted_success = base_success_rate * context_multiplier * time_multiplier * proficiency_multiplier
        return min(1.0, max(0.0, predicted_success))

    def _get_historical_success_rate(self, task_type: str) -> float:
        """获取历史成功率"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) as total, SUM(success) as successful
                FROM experiences
                WHERE task_type = ?
            ''', (task_type,))

            row = cursor.fetchone()
            if row and row[0] > 0:
                return row[1] / row[0]
            else:
                return 0.5  # 默认成功率

    def _calculate_context_multiplier(self, context: Dict[str, Any]) -> float:
        """计算上下文乘数"""
        # 基于上下文信息调整预测
        multiplier = 1.0

        # 如果是高峰期，稍微降低成功率
        if context.get('is_peak_hour', False):
            multiplier *= 0.95

        # 如果有相关经验，提高成功率
        if context.get('has_similar_experience', False):
            multiplier *= 1.1

        return multiplier

    def _calculate_time_multiplier(self) -> float:
        """计算时间乘数"""
        current_hour = datetime.now().hour

        # 基于历史数据，某些时间段表现更好
        if 9 <= current_hour <= 17:  # 白天工作时间
            return 1.05
        elif 22 <= current_hour or current_hour <= 6:  # 深夜
            return 0.9
        else:
            return 1.0

    def recommend_learning_path(self) -> List[str]:
        """推荐学习路径"""
        recommendations = []

        # 识别薄弱环节
        weak_skills = [skill for skill, prof in self.skill_proficiency.items() if prof < 0.6]
        recommendations.extend(weak_skills)

        # 识别高频但成功率低的任务
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT task_type,
                       COUNT(*) as total,
                       AVG(success) as success_rate
                FROM experiences
                GROUP BY task_type
                HAVING total > 5 AND success_rate < 0.7
                ORDER BY total DESC
                LIMIT 5
            ''')

            for row in cursor:
                recommendations.append(f"improve_{row[0]}")

        return list(set(recommendations))  # 去重

    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        insights = {
            'total_experiences': len(self.experience_memory),
            'skill_proficiencies': dict(self.skill_proficiency),
            'learning_patterns': dict(self.learning_patterns),
            'recommendations': self.recommend_learning_path()
        }

        # 计算学习效率
        if self.experience_memory:
            recent_experiences = [exp for exp in self.experience_memory[-100:]]  # 最近100个经验
            success_rate = sum(1 for exp in recent_experiences if exp['success']) / len(recent_experiences)
            avg_duration = sum(exp['duration'] for exp in recent_experiences) / len(recent_experiences)

            insights['recent_performance'] = {
                'success_rate': success_rate,
                'avg_duration': avg_duration,
                'learning_efficiency': success_rate / max(avg_duration, 1)  # 效率指标
            }

        return insights
