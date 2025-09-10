from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO
import json
import os
import sys
from datetime import datetime
import threading
import time
import logging

# 确保typing正确导入
try:
    from typing import Dict, List, Any, Optional
except ImportError:
    # 如果typing导入失败，手动定义Optional
    Optional = type(None)

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.model_manager import ModelManager
from src.mcp_manager import MCPManager
from src.task_history_manager import TaskHistoryManager
from src.performance_monitor import PerformanceMonitor
from src.config_manager import ConfigManager
from src.plugin_manager import PluginManager
from src.data_visualizer import DataVisualizer

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局系统实例 - 延迟初始化
agent_system = None

def get_agent_system():
    """延迟初始化系统实例"""
    global agent_system
    if agent_system is None:
        agent_system = WebAgentSystem()
    return agent_system

class WebAgentSystem:
    def __init__(self):
        self.model_manager = ModelManager()
        self.mcp_manager = MCPManager()
        self.task_history = TaskHistoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager(plugin_dir=os.path.join(os.path.dirname(__file__), 'plugins'))
        self.data_visualizer = DataVisualizer()

        # 自动加载插件
        self._load_plugins()

        # 性能监控默认不启动，由用户手动控制
        # self._start_performance_monitoring()

    def _start_performance_monitoring(self):
        """启动性能监控"""
        try:
            self.performance_monitor.start_monitoring(interval=2.0)  # 每2秒监控一次
            print("✅ 性能监控已启动")
        except Exception as e:
            print(f"❌ 性能监控启动失败: {e}")

    def _load_plugins(self):
        """自动发现并加载插件"""
        try:
            available_plugins = self.plugin_manager.discover_plugins()
            print(f"发现插件: {available_plugins}")

            loaded_count = 0
            for plugin_name in available_plugins:
                if self.plugin_manager.load_plugin(plugin_name):
                    loaded_count += 1
                    print(f"✅ 插件 {plugin_name} 加载成功")
                else:
                    print(f"❌ 插件 {plugin_name} 加载失败")

            print(f"插件加载完成: {loaded_count}/{len(available_plugins)} 个插件已加载")

        except Exception as e:
            print(f"插件自动加载失败: {e}")

    def get_system_status(self):
        """获取系统状态"""
        models = self.model_manager.get_available_models()
        # 确保返回格式为数组（兼容前端）
        return {
            'timestamp': datetime.now().isoformat(),
            'models': models,
            'performance': self.performance_monitor.get_current_metrics(),
            'plugins': self.plugin_manager.list_plugins(),
            'tasks': self.task_history.get_recent_tasks(10)
        }

    def process_task(self, task_description, model_name=None):
        """处理任务：增强版 - 支持自动能力学习"""
        try:
            # 1. 检测是否需要特定能力（实时数据查询等）
            capability_needed = self.detect_capability_need(task_description)
            
            if capability_needed:
                print(f"🔍 检测到需要特殊能力: {capability_needed}")
                
                # 2. 尝试自动学习并执行
                learned_result = self.auto_learn_and_execute(task_description, capability_needed)
                
                if learned_result['status'] == 'success':
                    # 保存任务历史
                    self.task_history.add_task({
                        'task': task_description,
                        'result': learned_result['result'],
                        'timestamp': datetime.now().isoformat(),
                        'type': 'learned_capability',
                        'capability': capability_needed
                    })
                    
                    return {
                        'status': 'success',
                        'task': task_description,
                        'model': 'auto_learned',
                        'capability': capability_needed,
                        'result': learned_result['result']
                    }
                else:
                    print(f"⚠️ 自动学习失败，回退到普通模型: {learned_result.get('error')}")
            
            # 3. 检查是否是@查询
            if task_description.startswith('@'):
                result = self.mcp_manager.search_remote_mcp(task_description)
                return {
                    'status': 'success',
                    'task': task_description,
                    'model': 'mcp',
                    'result': result
                }
            
            # 4. 使用模型处理
            model = model_name or getattr(self.config_manager, 'default_model', None) or 'qwen3'
            result = self.model_manager.call_model(model, task_description)
            
            return {
                'status': 'success',
                'task': task_description,
                'model': model,
                'result': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': task_description,
                'model': model_name,
                'error': str(e)
            }

    def detect_capability_need(self, query):
        """检测是否需要特定能力（实时数据查询）"""
        query_lower = query.lower()
        
        # 检测机票查询
        if any(word in query_lower for word in ['机票', '航班', '飞机票', '机票价格']):
            return 'flight_price_query'
        
        # 检测酒店查询
        if any(word in query_lower for word in ['酒店', '酒店价格', '住宿', '预订酒店']):
            return 'hotel_price_query'
        
        # 检测股票查询
        if any(word in query_lower for word in ['股票', '股价', '股票价格']):
            return 'stock_price_query'
        
        # 检测天气查询
        if any(word in query_lower for word in ['天气', '天气预报', '气温']):
            return 'weather_query'
        
        # 检测实时新闻
        if any(word in query_lower for word in ['新闻', '最新消息', '今日新闻']):
            return 'news_query'
        
        # 检测热搜查询
        if any(word in query_lower for word in ['热搜', '百度热搜', '微博热搜', '热门话题', '热点']):
            return 'trending_search_query'
        
        # 检测网络爬虫相关查询
        if any(word in query_lower for word in ['爬取', '抓取', '采集', '网页内容']):
            return 'web_scraping_query'
        
        return None
    
    def auto_learn_and_execute(self, query, capability):
        """自动学习并执行特定能力"""
        try:
            # 构造学习查询
            learning_queries = {
                'flight_price_query': f'@web 实时查询机票价格 API 代码示例 {query}',
                'hotel_price_query': f'@web 实时查询酒店价格 API 代码示例 {query}', 
                'stock_price_query': f'@web 实时查询股票价格 API 代码示例 {query}',
                'weather_query': f'@web 实时查询天气API 代码示例 {query}',
                'news_query': f'@web 实时查询新闻API 代码示例 {query}',
                'trending_search_query': f'@web 实时查询百度热搜微博热搜 API 代码示例 {query}',
                'web_scraping_query': f'@web 网页爬虫数据抓取 API 代码示例 {query}'
            }
            
            learning_query = learning_queries.get(capability, f'@web {query} API代码示例')
            
            # 使用模型管理器的发现并尝试功能
            result = self.model_manager.discover_and_attempt(learning_query)
            
            if result['status'] == 'ok':
                return {
                    'status': 'success',
                    'result': f"✅ 通过MCP学习新能力并实时执行成功！\n\n查询: {query}\n\n{result['result']}\n\n🎯 系统已自动学会并执行了{capability}功能",
                    'model': 'auto_learned_executed'
                }
            elif result['status'] == 'requires_review':
                # 对于需要审查的代码，返回学习到的内容但不执行
                return {
                    'status': 'success', 
                    'result': f"🤖 通过MCP学习到处理方法（需人工确认）:\n\n查询: {query}\n\n学习到的代码:\n```python\n{result.get('raw_code', 'N/A')}\n```\n\n⚠️ 此代码包含网络操作，需要人工审查后执行",
                    'model': 'auto_learned'
                }
            elif result['status'] in ['timeout', 'exec_error', 'no_data']:
                # 执行出错时，提供代码和错误信息
                error_msg = result.get('error', result.get('result', '执行失败'))
                fallback_code = result.get('fallback_code', result.get('code', ''))
                
                return {
                    'status': 'success',
                    'result': f"🤖 通过MCP学习到处理方法，但执行遇到问题:\n\n查询: {query}\n\n❌ 执行结果: {error_msg}\n\n💻 学习到的代码:\n```python\n{fallback_code}\n```\n\n💡 建议: 请检查网络连接或手动执行代码",
                    'model': 'auto_learned_with_error'
                }
            else:
                # 返回MCP的原始响应作为回退
                raw_response = result.get('raw', '未找到相关解决方案')
                return {
                    'status': 'success',
                    'result': f"🔍 MCP搜索结果:\n\n查询: {query}\n\n{raw_response}\n\n💡 建议: 系统正在学习如何处理此类请求，当前提供相关信息供参考。",
                    'model': 'mcp_search'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': f"自动学习失败: {str(e)}"
            }

# 路由定义
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    try:
        system = get_agent_system()
        status = system.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models')
def get_models():
    """获取可用模型列表"""
    try:
        system = get_agent_system()
        models = system.model_manager.get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>')
def get_model_info(model_name):
    """获取模型详细信息"""
    try:
        system = get_agent_system()
        model_info = system.model_manager.get_model_config(model_name)
        return jsonify(model_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>/test', methods=['POST'])
def test_model(model_name):
    """测试模型"""
    try:
        system = get_agent_system()
        test_result = system.model_manager.test_model(model_name)
        return jsonify(test_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>/config', methods=['PUT'])
def update_model_config(model_name):
    """更新模型配置"""
    try:
        config = request.get_json()
        system = get_agent_system()
        success = system.model_manager.update_model_config(model_name, config)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 向后兼容路由：保留旧的 /api/task 路径，代理到新的 /api/tasks 处理逻辑
@app.route('/api/task', methods=['POST'])
def process_task_compat():
    """向后兼容：旧脚本可能调用 /api/task，直接代理到新的任务处理代码"""
    try:
        # 直接复用 /api/tasks 的处理逻辑
        data = request.get_json()
        task_description = data.get('task') if data else None
        model_name = data.get('model') if data else None

        system = get_agent_system()
        result = system.process_task(task_description, model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def process_task():
    """处理任务"""
    try:
        data = request.get_json()
        task_description = data.get('task')
        model_name = data.get('model')

        system = get_agent_system()
        result = system.process_task(task_description, model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """获取任务历史"""
    try:
        limit = int(request.args.get('limit', 50))
        system = get_agent_system()
        history = system.task_history.get_recent_tasks(limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<task_id>')
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        system = get_agent_system()
        task = system.task_history.get_task_by_id(task_id)
        return jsonify(task)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/stats')
def get_history_stats():
    """获取历史统计"""
    try:
        days = int(request.args.get('days', 7))
        system = get_agent_system()
        stats = system.task_history.get_task_statistics(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins')
def get_plugins():
    """获取插件列表"""
    try:
        system = get_agent_system()
        plugins = system.plugin_manager.list_plugins()
        stats = system.plugin_manager.get_plugin_stats()
        return jsonify({'plugins': plugins, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    """获取性能监控数据"""
    try:
        system = get_agent_system()
        current_metrics = system.performance_monitor.get_current_metrics()
        health_score = system.performance_monitor.get_system_health_score()
        return jsonify({
            'current_metrics': current_metrics,
            'health_score': health_score,
            'alerts': system.performance_monitor.alerts[-10:]  # 最近10个告警
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance/history')
def get_performance_history():
    """获取性能历史数据"""
    try:
        minutes = int(request.args.get('minutes', 60))
        system = get_agent_system()
        history = system.performance_monitor.get_metrics_history(minutes)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance/report')
def get_performance_report():
    """获取性能报告"""
    try:
        minutes = int(request.args.get('minutes', 60))
        system = get_agent_system()
        report = system.performance_monitor.get_performance_report(minutes)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance/start', methods=['POST'])
def start_performance_monitoring():
    """启动性能监控"""
    try:
        interval = float(request.args.get('interval', 1.0))
        system = get_agent_system()
        system.performance_monitor.start_monitoring(interval)
        return jsonify({'message': '性能监控已启动'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance/stop', methods=['POST'])
def stop_performance_monitoring():
    """停止性能监控"""
    try:
        system = get_agent_system()
        system.performance_monitor.stop_monitoring()
        return jsonify({'message': '性能监控已停止'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance/threshold/<metric>', methods=['PUT'])
def update_performance_threshold(metric):
    """更新性能阈值"""
    try:
        data = request.get_json()
        value = data.get('value')
        if value is None:
            return jsonify({'error': '缺少value参数'}), 400

        system = get_agent_system()
        system.performance_monitor.set_threshold(metric, float(value))
        return jsonify({'message': f'阈值已更新: {metric} = {value}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("启动Web应用...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
