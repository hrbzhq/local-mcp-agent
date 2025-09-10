"""
MCP进化优化器 - MCP Evolution Optimizer
实现MCP自主优化，质量与数量的双重进化
"""

import os
import json
import time
import logging
import threading
import importlib
import inspect
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
import sqlite3
import ast
import re

class MCPEvolutionOptimizer:
    """MCP进化优化器"""

    def __init__(self, mcp_directory: str = None, db_path: str = None):
        self.mcp_directory = mcp_directory or os.path.join(os.path.dirname(__file__), '..', 'plugins')
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', 'mcp', 'mcp_evolution.db')
        self.modules = {}  # 已加载的模块
        self.module_usage_stats = defaultdict(dict)  # 模块使用统计
        self.quality_metrics = {}  # 质量指标
        self.evolution_active = False
        self.evolution_thread = None
        self.init_database()

    def init_database(self):
        """初始化MCP进化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS module_quality (
                    id INTEGER PRIMARY KEY,
                    module_name TEXT,
                    timestamp TIMESTAMP,
                    code_quality REAL,
                    performance REAL,
                    reliability REAL,
                    maintainability REAL,
                    overall_score REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS evolution_actions (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    action_type TEXT,
                    module_name TEXT,
                    description TEXT,
                    result TEXT,
                    metrics TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS requirement_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern TEXT,
                    frequency INTEGER,
                    last_seen TIMESTAMP,
                    category TEXT
                )
            ''')

    def start_evolution(self):
        """启动MCP进化"""
        if not self.evolution_active:
            self.evolution_active = True
            self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
            self.evolution_thread.start()
            logging.info("MCP进化优化已启动")

    def stop_evolution(self):
        """停止MCP进化"""
        self.evolution_active = False
        logging.info("MCP进化优化已停止")

    def _evolution_loop(self):
        """进化主循环"""
        while self.evolution_active:
            try:
                # 1. 分析模块使用情况
                self._analyze_module_usage()

                # 2. 评估模块质量
                self._assess_module_quality()

                # 3. 发现新需求
                new_requirements = self._discover_new_requirements()

                # 4. 制定进化计划
                evolution_plan = self._create_evolution_plan(new_requirements)

                # 5. 执行进化
                self._execute_evolution_plan(evolution_plan)

                # 等待下一轮进化（每2小时检查一次）
                time.sleep(7200)

            except Exception as e:
                logging.error(f"MCP进化循环出错: {e}")
                time.sleep(600)  # 出错后等待10分钟

    def _analyze_module_usage(self):
        """分析模块使用情况"""
        # 扫描插件目录
        if os.path.exists(self.mcp_directory):
            for filename in os.listdir(self.mcp_directory):
                if filename.endswith('.py') and not filename.startswith('__'):
                    module_name = filename[:-3]  # 移除.py扩展名
                    self._analyze_single_module(module_name)

        # 按使用频率排序
        sorted_modules = sorted(
            self.module_usage_stats.items(),
            key=lambda x: x[1].get('usage_count', 0),
            reverse=True
        )

        logging.info(f"分析了 {len(sorted_modules)} 个MCP模块的使用情况")

    def _analyze_single_module(self, module_name: str):
        """分析单个模块"""
        try:
            # 动态导入模块
            module_path = f"plugins.{module_name}"
            module = importlib.import_module(module_path)

            # 分析模块结构
            classes = []
            functions = []

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and not name.startswith('_'):
                    classes.append(name)
                elif inspect.isfunction(obj) and not name.startswith('_'):
                    functions.append(name)

            # 获取或初始化使用统计
            if module_name not in self.module_usage_stats:
                self.module_usage_stats[module_name] = {
                    'usage_count': 0,
                    'last_used': None,
                    'classes': classes,
                    'functions': functions,
                    'file_size': 0,
                    'complexity': 0
                }

            # 更新文件大小
            module_file = os.path.join(self.mcp_directory, f"{module_name}.py")
            if os.path.exists(module_file):
                self.module_usage_stats[module_name]['file_size'] = os.path.getsize(module_file)

        except Exception as e:
            logging.warning(f"分析模块 {module_name} 时出错: {e}")

    def _assess_module_quality(self):
        """评估模块质量"""
        for module_name, stats in self.module_usage_stats.items():
            try:
                quality_score = self._calculate_quality_score(module_name, stats)
                self.quality_metrics[module_name] = quality_score

                # 记录质量指标
                self._record_quality_metrics(module_name, quality_score)

            except Exception as e:
                logging.error(f"评估模块 {module_name} 质量时出错: {e}")

    def _calculate_quality_score(self, module_name: str, stats: Dict[str, Any]) -> Dict[str, float]:
        """计算质量分数"""
        # 读取模块文件
        module_file = os.path.join(self.mcp_directory, f"{module_name}.py")
        if not os.path.exists(module_file):
            return {'overall': 0.0}

        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 代码质量指标
            lines_of_code = len(content.split('\n'))
            comment_lines = len(re.findall(r'#.*', content))
            docstring_count = len(re.findall(r'""".*?"""', content, re.DOTALL))

            # 复杂度评估（简化版）
            function_count = len(stats.get('classes', [])) + len(stats.get('functions', []))
            import_count = len(re.findall(r'^import|^from.*import', content, re.MULTILINE))

            # 计算各项指标
            code_quality = min(1.0, (comment_lines + docstring_count * 2) / max(lines_of_code, 1))
            performance = 1.0 / (1.0 + function_count / 10.0)  # 复杂度惩罚
            reliability = min(1.0, stats.get('usage_count', 0) / 100.0)  # 使用频率
            maintainability = min(1.0, (lines_of_code / 1000.0))  # 代码规模

            overall_score = (code_quality + performance + reliability + maintainability) / 4.0

            return {
                'code_quality': code_quality,
                'performance': performance,
                'reliability': reliability,
                'maintainability': maintainability,
                'overall': overall_score
            }

        except Exception as e:
            logging.warning(f"计算模块 {module_name} 质量分数时出错: {e}")
            return {'overall': 0.5}

    def _discover_new_requirements(self) -> List[Dict[str, Any]]:
        """发现新需求"""
        requirements = []

        # 分析使用模式，识别缺失的功能
        usage_patterns = self._analyze_usage_patterns()

        # 识别高频但质量低的模块
        low_quality_modules = [
            name for name, quality in self.quality_metrics.items()
            if quality.get('overall', 0) < 0.6
        ]

        # 生成改进需求
        for module in low_quality_modules:
            requirements.append({
                'type': 'quality_improvement',
                'module': module,
                'description': f"改进模块 {module} 的质量",
                'priority': 2,
                'estimated_effort': 3
            })

        # 识别新兴需求模式
        for pattern, frequency in usage_patterns.items():
            if frequency > 5 and not self._module_exists_for_pattern(pattern):
                requirements.append({
                    'type': 'new_module',
                    'pattern': pattern,
                    'description': f"为模式 {pattern} 创建新模块",
                    'priority': 1,
                    'estimated_effort': 5
                })

        return requirements

    def _analyze_usage_patterns(self) -> Dict[str, int]:
        """分析使用模式"""
        patterns = defaultdict(int)

        # 这里可以从任务历史中提取模式
        # 目前使用预定义的常见模式
        common_patterns = {
            'data_processing': 15,
            'api_integration': 12,
            'file_management': 10,
            'web_interaction': 8,
            'database_operations': 6
        }

        return common_patterns

    def _module_exists_for_pattern(self, pattern: str) -> bool:
        """检查是否存在处理该模式的模块"""
        pattern_keywords = pattern.lower().split('_')
        for module_name in self.module_usage_stats.keys():
            module_keywords = module_name.lower().split('_')
            if any(keyword in module_keywords for keyword in pattern_keywords):
                return True
        return False

    def _create_evolution_plan(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """制定进化计划"""
        plan = []

        # 按优先级排序需求
        sorted_requirements = sorted(requirements, key=lambda x: x['priority'])

        # 只处理高优先级需求
        for req in sorted_requirements[:2]:  # 每次最多处理2个进化任务
            if req['type'] == 'quality_improvement':
                plan.append({
                    'type': 'module_refactor',
                    'module': req['module'],
                    'description': req['description'],
                    'estimated_effort': req['estimated_effort'],
                    'priority': req['priority']
                })
            elif req['type'] == 'new_module':
                plan.append({
                    'type': 'module_creation',
                    'pattern': req['pattern'],
                    'description': req['description'],
                    'estimated_effort': req['estimated_effort'],
                    'priority': req['priority']
                })

        return plan

    def _execute_evolution_plan(self, plan: List[Dict[str, Any]]):
        """执行进化计划"""
        for action in plan:
            try:
                if action['type'] == 'module_refactor':
                    self._refactor_module(action['module'])
                elif action['type'] == 'module_creation':
                    self._create_new_module(action['pattern'])

                # 记录进化历史
                self._record_evolution_history(action, 'success')

            except Exception as e:
                logging.error(f"执行进化动作失败: {e}")
                self._record_evolution_history(action, 'failed', str(e))

    def _refactor_module(self, module_name: str):
        """重构模块"""
        logging.info(f"开始重构模块: {module_name}")

        # 这里可以实现具体的重构逻辑
        # 例如：代码优化、结构改进、性能提升等

        # 模拟重构过程
        time.sleep(2)

        logging.info(f"模块 {module_name} 重构完成")

    def _create_new_module(self, pattern: str):
        """创建新模块"""
        logging.info(f"开始创建新模块用于模式: {pattern}")

        # 生成模块名称
        module_name = f"{pattern}_handler"

        # 创建基本的模块模板
        self._generate_module_template(module_name, pattern)

        logging.info(f"新模块 {module_name} 创建完成")

    def _generate_module_template(self, module_name: str, pattern: str):
        """生成模块模板"""
        template = f'''"""
{pattern.replace('_', ' ').title()} Handler
自动生成的MCP模块
"""

import logging
from typing import Dict, List, Any, Optional

class {pattern.title().replace('_', '')}Handler:
    """{pattern.replace('_', ' ').title()} 处理模块"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理{pattern}相关的数据"""
        try:
            # TODO: 实现具体的处理逻辑
            result = {{
                "status": "success",
                "pattern": "{pattern}",
                "processed_data": data,
                "timestamp": "auto_generated"
            }}

            self.logger.info(f"成功处理{pattern}数据")
            return result

        except Exception as e:
            self.logger.error(f"处理{pattern}数据时出错: {{e}}")
            return {{
                "status": "error",
                "error": str(e),
                "pattern": "{pattern}"
            }}

def handle_{pattern}(data: Dict[str, Any]) -> Dict[str, Any]:
    """{pattern}处理函数"""
    handler = {pattern.title().replace('_', '')}Handler()
    return handler.process(data)
'''

        # 写入文件
        module_path = os.path.join(self.mcp_directory, f"{module_name}.py")
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(template)

    def _record_quality_metrics(self, module_name: str, quality_score: Dict[str, float]):
        """记录质量指标"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO module_quality
                (module_name, timestamp, code_quality, performance, reliability, maintainability, overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                module_name,
                datetime.now().isoformat(),
                quality_score.get('code_quality', 0),
                quality_score.get('performance', 0),
                quality_score.get('reliability', 0),
                quality_score.get('maintainability', 0),
                quality_score.get('overall_score', 0)
            ))

    def _record_evolution_history(self, action: Dict[str, Any], result: str, error: str = None):
        """记录进化历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO evolution_actions
                (timestamp, action_type, module_name, description, result, metrics)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                action.get('type', ''),
                action.get('module', action.get('pattern', '')),
                action.get('description', ''),
                result,
                json.dumps({'error': error} if error else {})
            ))

    def record_module_usage(self, module_name: str, success: bool = True):
        """记录模块使用情况"""
        if module_name in self.module_usage_stats:
            self.module_usage_stats[module_name]['usage_count'] += 1
            self.module_usage_stats[module_name]['last_used'] = datetime.now().isoformat()

    def get_evolution_status(self) -> Dict[str, Any]:
        """获取进化状态"""
        return {
            'active': self.evolution_active,
            'module_count': len(self.module_usage_stats),
            'quality_assessed': len(self.quality_metrics),
            'avg_quality': sum(q.get('overall', 0) for q in self.quality_metrics.values()) / max(len(self.quality_metrics), 1)
        }
