import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

class TaskHistoryManager:
    """任务历史管理模块"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'mcp', 'task_history.db')
        self.db_path = os.path.abspath(db_path)
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY,
                    task_input TEXT NOT NULL,
                    task_type TEXT,
                    complexity TEXT,
                    model_used TEXT,
                    mcp_used TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    result TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS task_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern TEXT UNIQUE,
                    frequency INTEGER DEFAULT 1,
                    avg_execution_time REAL,
                    success_rate REAL,
                    last_used TIMESTAMP
                )
            ''')

    def record_task(self, task_data: Dict[str, Any]):
        """记录任务执行结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO task_history
                (task_input, task_type, complexity, model_used, mcp_used,
                 execution_time, success, result, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_data.get('task_input', ''),
                task_data.get('task_type', ''),
                task_data.get('complexity', ''),
                task_data.get('model_used', ''),
                task_data.get('mcp_used', ''),
                task_data.get('execution_time', 0),
                task_data.get('success', False),
                json.dumps(task_data.get('result', '')) if isinstance(task_data.get('result'), dict) else task_data.get('result', ''),
                json.dumps(task_data.get('error_message', '')) if isinstance(task_data.get('error_message'), dict) else task_data.get('error_message', '')
            ))

        # 更新任务模式统计
        self.update_task_patterns(task_data)

    def add_task(self, task_data: Dict[str, Any]):
        """添加任务记录 - 兼容方法，调用record_task"""
        # 规范化任务数据格式
        normalized_data = {
            'task_input': task_data.get('task', task_data.get('query', task_data.get('task_input', ''))),
            'task_type': task_data.get('type', task_data.get('task_type', 'unknown')),
            'complexity': task_data.get('complexity', 'unknown'),
            'model_used': task_data.get('model', task_data.get('model_used', 'unknown')),
            'mcp_used': task_data.get('mcp_used', ''),
            'execution_time': task_data.get('execution_time', 0),
            'success': task_data.get('status') == 'success' or task_data.get('success', True),
            'result': task_data.get('result', ''),
            'error_message': task_data.get('error', task_data.get('error_message', ''))
        }
        
        # 添加时间戳
        if 'timestamp' in task_data:
            normalized_data['created_at'] = task_data['timestamp']
        
        self.record_task(normalized_data)

    def update_task_patterns(self, task_data: Dict[str, Any]):
        """更新任务模式统计"""
        task_input = task_data.get('task_input', '')
        # 简单的模式提取（可以改进为更智能的模式识别）
        pattern = self.extract_pattern(task_input)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, frequency, avg_execution_time, success_rate
                FROM task_patterns WHERE pattern = ?
            ''', (pattern,))

            existing = cursor.fetchone()

            if existing:
                pattern_id, freq, avg_time, success_rate = existing
                new_freq = freq + 1
                new_avg_time = (avg_time * freq + task_data.get('execution_time', 0)) / new_freq
                new_success_rate = (success_rate * freq + (1 if task_data.get('success') else 0)) / new_freq

                conn.execute('''
                    UPDATE task_patterns
                    SET frequency = ?, avg_execution_time = ?, success_rate = ?, last_used = ?
                    WHERE id = ?
                ''', (new_freq, new_avg_time, new_success_rate, datetime.now(), pattern_id))
            else:
                conn.execute('''
                    INSERT INTO task_patterns (pattern, frequency, avg_execution_time, success_rate, last_used)
                    VALUES (?, 1, ?, ?, ?)
                ''', (pattern, task_data.get('execution_time', 0),
                      1 if task_data.get('success') else 0, datetime.now()))

    def extract_pattern(self, task_input: str) -> str:
        """提取任务模式"""
        # 简单的关键词模式提取
        keywords = []
        if '代码' in task_input or '编程' in task_input:
            keywords.append('编程')
        if '分析' in task_input or '数据' in task_input:
            keywords.append('分析')
        if '设计' in task_input or '架构' in task_input:
            keywords.append('设计')
        if '优化' in task_input or '改进' in task_input:
            keywords.append('优化')

        return '_'.join(keywords) if keywords else '其他'

    def get_task_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取任务统计信息"""
        since_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # 总体统计
            cursor = conn.execute('''
                SELECT COUNT(*), AVG(execution_time), SUM(success), COUNT(*)
                FROM task_history
                WHERE created_at >= ?
            ''', (since_date,))

            total_tasks, avg_time, success_count, total_count = cursor.fetchone()
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0

            # 任务类型分布
            cursor = conn.execute('''
                SELECT task_type, COUNT(*)
                FROM task_history
                WHERE created_at >= ? AND task_type IS NOT NULL
                GROUP BY task_type
                ORDER BY COUNT(*) DESC
            ''', (since_date,))

            task_types = dict(cursor.fetchall())

            # 模型使用统计
            cursor = conn.execute('''
                SELECT model_used, COUNT(*)
                FROM task_history
                WHERE created_at >= ? AND model_used IS NOT NULL
                GROUP BY model_used
                ORDER BY COUNT(*) DESC
            ''', (since_date,))

            model_usage = dict(cursor.fetchall())

            # 热门任务模式
            cursor = conn.execute('''
                SELECT pattern, frequency, avg_execution_time, success_rate
                FROM task_patterns
                ORDER BY frequency DESC
                LIMIT 10
            ''',)

            patterns = cursor.fetchall()

        return {
            'total_tasks': total_tasks or 0,
            'avg_execution_time': avg_time or 0,
            'success_rate': success_rate,
            'task_types': task_types,
            'model_usage': model_usage,
            'popular_patterns': patterns,
            'period_days': days
        }

    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的任务记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, task_input, task_type, complexity, model_used, mcp_used,
                       execution_time, success, result, error_message, created_at
                FROM task_history
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            tasks = []
            for row in cursor.fetchall():
                task = {
                    'id': row[0],
                    'task_input': row[1],
                    'task_type': row[2],
                    'complexity': row[3],
                    'model_used': row[4],
                    'mcp_used': row[5],
                    'execution_time': row[6],
                    'success': bool(row[7]),
                    'result': json.loads(row[8]) if row[8] and row[8].startswith('{') else row[8],
                    'error_message': json.loads(row[9]) if row[9] and row[9].startswith('{') else row[9],
                    'created_at': row[10]
                }
                tasks.append(task)

            return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务详情"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, task_input, task_type, complexity, model_used, mcp_used,
                       execution_time, success, result, error_message, created_at
                FROM task_history
                WHERE id = ?
            ''', (task_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'task_input': row[1],
                    'task_type': row[2],
                    'complexity': row[3],
                    'model_used': row[4],
                    'mcp_used': row[5],
                    'execution_time': row[6],
                    'success': bool(row[7]),
                    'result': json.loads(row[8]) if row[8] and row[8].startswith('{') else row[8],
                    'error_message': json.loads(row[9]) if row[9] and row[9].startswith('{') else row[9],
                    'created_at': row[10]
                }
            return None

    def get_tasks_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取指定日期范围内的任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, task_input, task_type, complexity, model_used, mcp_used,
                       execution_time, success, result, error_message, created_at
                FROM task_history
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
            ''', (start_date, end_date))

            tasks = []
            for row in cursor.fetchall():
                task = {
                    'id': row[0],
                    'task_input': row[1],
                    'task_type': row[2],
                    'complexity': row[3],
                    'model_used': row[4],
                    'mcp_used': row[5],
                    'execution_time': row[6],
                    'success': bool(row[7]),
                    'result': json.loads(row[8]) if row[8] and row[8].startswith('{') else row[8],
                    'error_message': json.loads(row[9]) if row[9] and row[9].startswith('{') else row[9],
                    'created_at': row[10]
                }
                tasks.append(task)

            return tasks

    def get_tasks_by_model(self, model_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取指定模型的任务记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, task_input, task_type, complexity, model_used, mcp_used,
                       execution_time, success, result, error_message, created_at
                FROM task_history
                WHERE model_used = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (model_name, limit))

            tasks = []
            for row in cursor.fetchall():
                task = {
                    'id': row[0],
                    'task_input': row[1],
                    'task_type': row[2],
                    'complexity': row[3],
                    'model_used': row[4],
                    'mcp_used': row[5],
                    'execution_time': row[6],
                    'success': bool(row[7]),
                    'result': json.loads(row[8]) if row[8] and row[8].startswith('{') else row[8],
                    'error_message': json.loads(row[9]) if row[9] and row[9].startswith('{') else row[9],
                    'created_at': row[10]
                }
                tasks.append(task)

            return tasks

    def search_tasks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索任务记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, task_input, task_type, complexity, model_used, mcp_used,
                       execution_time, success, result, error_message, created_at
                FROM task_history
                WHERE task_input LIKE ? OR result LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))

            tasks = []
            for row in cursor.fetchall():
                task = {
                    'id': row[0],
                    'task_input': row[1],
                    'task_type': row[2],
                    'complexity': row[3],
                    'model_used': row[4],
                    'mcp_used': row[5],
                    'execution_time': row[6],
                    'success': bool(row[7]),
                    'result': json.loads(row[8]) if row[8] and row[8].startswith('{') else row[8],
                    'error_message': json.loads(row[9]) if row[9] and row[9].startswith('{') else row[9],
                    'created_at': row[10]
                }
                tasks.append(task)

            return tasks

    def delete_old_tasks(self, days: int = 30) -> int:
        """删除指定天数之前的任务记录"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM task_history
                WHERE created_at < ?
            ''', (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

    def export_tasks(self, start_date: str = None, end_date: str = None, format: str = 'json') -> str:
        """导出任务记录"""
        if start_date and end_date:
            tasks = self.get_tasks_by_date_range(start_date, end_date)
        else:
            tasks = self.get_recent_tasks(1000)  # 导出最近1000条记录

        if format == 'json':
            return json.dumps(tasks, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # 简单的CSV格式
            if not tasks:
                return "No tasks found"

            headers = list(tasks[0].keys())
            csv_lines = [','.join(headers)]

            for task in tasks:
                values = []
                for header in headers:
                    value = str(task.get(header, ''))
                    # 转义包含逗号的值
                    if ',' in value:
                        value = f'"{value}"'
                    values.append(value)
                csv_lines.append(','.join(values))

            return '\n'.join(csv_lines)

        return json.dumps(tasks, ensure_ascii=False, indent=2)

    def predict_task_complexity(self, task_input: str) -> str:
        """预测任务复杂度"""
        pattern = self.extract_pattern(task_input)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT AVG(avg_execution_time), AVG(success_rate)
                FROM task_patterns
                WHERE pattern = ?
            ''', (pattern,))

            result = cursor.fetchone()
            if result and result[0]:
                avg_time, success_rate = result
                if avg_time > 10:  # 超过10秒算复杂
                    return '复杂'
                elif avg_time > 3:  # 超过3秒算中等
                    return '中等'
                else:
                    return '简单'
            else:
                # 默认复杂度判断
                if len(task_input) > 200:
                    return '复杂'
                elif len(task_input) > 50:
                    return '中等'
                else:
                    return '简单'
