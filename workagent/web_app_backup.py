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
from typing import Dict, List, Any, Optional

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

# 全局系统实例
agent_system = None

def get_agent_system():
    """延迟初始化系统实例"""
    global agent_system
    if agent_system is None:
        agent_system = WebAgentSystem()
    return agent_system
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

    def _load_plugins(self):
        """自动发现并加载插件"""
        try:
            # 发现可用插件
            available_plugins = self.plugin_manager.discover_plugins()
            print(f"发现插件: {available_plugins}")
            
            # 加载每个插件
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
            import traceback
            traceback.print_exc()

    def get_system_status(self):
        """获取系统状态"""
        return {
            'timestamp': datetime.now().isoformat(),
            'models': self.model_manager.test_models(),
            'performance': self.performance_monitor.get_current_metrics(),
            'plugins': self.plugin_manager.list_plugins(),
            'tasks': self.task_history.get_recent_tasks(10)
        }

    def process_task(self, task_description, model_name=None):
        """智能处理任务 - 理解分析并调用MCP查询"""
        try:
            print(f"🔍 收到任务: {task_description}")

            # 1. 智能问题分析
            analysis = self._analyze_task(task_description)
            print(f"📊 任务分析: {analysis}")

            # 2. 尝试插件执行
            plugin_result = self._try_execute_plugin(task_description)
            if plugin_result:
                print("🔧 使用插件处理")
                response = plugin_result
            else:
                # 3. MCP查询增强
                mcp_results = self._query_mcp_services(task_description, analysis)
                if mcp_results:
                    print("🔗 发现MCP结果，整合信息")
                    # 整合MCP结果和模型响应
                    enhanced_prompt = self._build_enhanced_prompt(task_description, mcp_results, analysis)
                    response = self._call_model_with_context(model_name, enhanced_prompt)
                else:
                    # 4. 标准模型处理
                    print("🤖 使用模型处理")
                    response = self._call_model_with_context(model_name, task_description)

            # 5. 记录任务历史
            self.task_history.record_task({
                'task_input': task_description,
                'model_used': model_name or 'qwen3',
                'analysis': analysis,
                'result': response,
                'success': True
            })

            return {'status': 'success', 'response': response, 'analysis': analysis}

        except Exception as e:
            print(f"❌ 任务处理失败: {e}")
            return {'status': 'error', 'response': str(e)}

    def _analyze_task(self, task_description):
        """智能分析任务类型和需求"""
        analysis = {
            'task_type': 'general',
            'keywords': [],
            'entities': [],
            'intent': 'unknown',
            'complexity': 'simple',
            'requires_external_data': False,
            'is_at_query': False
        }

        task_lower = task_description.lower()

        # 检查是否为@查询
        if task_description.strip().startswith('@'):
            analysis['is_at_query'] = True
            analysis['requires_external_data'] = True
            analysis['task_type'] = 'at_query'
            analysis['intent'] = 'mcp_query'
            print(f"🎯 检测到@查询: {task_description}")

        # 分析关键词
        keywords = []
        if any(word in task_lower for word in ['查询', '查找', '搜索', '获取']):
            keywords.append('query')
        if any(word in task_lower for word in ['分析', '解析', '理解']):
            keywords.append('analysis')
        if any(word in task_lower for word in ['比较', '对比']):
            keywords.append('comparison')
        if any(word in task_lower for word in ['总结', '摘要']):
            keywords.append('summary')

        # 分析任务类型（仅当不是@查询时）
        if not analysis['is_at_query']:
            if any(word in task_lower for word in ['网页', '网站', '抓取', '爬取']):
                analysis['task_type'] = 'web_scraping'
                analysis['requires_external_data'] = True
            elif any(word in task_lower for word in ['高铁', '火车', '列车', '时刻表', '车次']):
                analysis['task_type'] = 'train_schedule'
                analysis['requires_external_data'] = True
            elif any(word in task_lower for word in ['数据库', '数据', '查询']):
                analysis['task_type'] = 'database'
            elif any(word in task_lower for word in ['文件', '文档', '读取']):
                analysis['task_type'] = 'file_processing'
            elif any(word in task_lower for word in ['api', '接口']):
                analysis['task_type'] = 'api_call'
            elif any(word in task_lower for word in ['代码', '编程', '开发']):
                analysis['task_type'] = 'coding'
            elif any(word in task_lower for word in ['数学', '计算']):
                analysis['task_type'] = 'mathematical'

        # 分析复杂度
        if len(task_description.split()) > 20 or '?' in task_description:
            analysis['complexity'] = 'complex'

        # 提取实体（URL、文件名等）
        import re
        urls = re.findall(r'https?://[^\s]+', task_description)
        if urls:
            analysis['entities'].extend(urls)
            analysis['requires_external_data'] = True

        analysis['keywords'] = keywords
        analysis['intent'] = 'query' if 'query' in keywords else 'analysis' if 'analysis' in keywords else 'general'

        return analysis

    def _query_mcp_services(self, task_description, analysis):
        """查询MCP服务获取相关信息"""
        mcp_results = []

        try:
            # 处理@查询 - 最高优先级
            if analysis.get('is_at_query', False):
                print(f"🎯 处理@查询: {task_description}")
                mcp_result = self.mcp_manager.search_remote_mcp(task_description)
                if mcp_result:
                    mcp_results.append({
                        'type': 'at_query',
                        'query': task_description,
                        'content': mcp_result
                    })
                return mcp_results  # @查询直接返回，不再处理其他类型

            # 根据任务类型查询相关MCP
            if analysis['task_type'] == 'web_scraping' and analysis['entities']:
                # Web抓取相关的MCP查询
                for url in analysis['entities']:
                    mcp_result = self.mcp_manager.search_remote_mcp(f"web_content:{url}")
                    if mcp_result:
                        mcp_results.append({
                            'type': 'web_content',
                            'source': url,
                            'content': mcp_result
                        })

            elif analysis['task_type'] == 'train_schedule':
                # 高铁时刻表查询
                import re
                # 提取车次号
                train_match = re.search(r'(\d+)', task_description)
                if train_match:
                    train_number = train_match.group(1)
                    mcp_result = self.mcp_manager.search_remote_mcp(f"train_schedule:{train_number}")
                    if mcp_result:
                        mcp_results.append({
                            'type': 'train_schedule',
                            'train_number': train_number,
                            'content': mcp_result
                        })

            elif analysis['task_type'] == 'coding':
                # 编程相关的MCP查询
                mcp_result = self.mcp_manager.search_remote_mcp(f"code_examples:{task_description[:50]}")
                if mcp_result:
                    mcp_results.append({
                        'type': 'code_examples',
                        'content': mcp_result
                    })

            elif analysis['requires_external_data']:
                # 通用外部数据查询
                mcp_result = self.mcp_manager.search_remote_mcp(task_description[:100])
                if mcp_result:
                    mcp_results.append({
                        'type': 'general_knowledge',
                        'content': mcp_result
                    })

        except Exception as e:
            print(f"MCP查询失败: {e}")

        return mcp_results

    def _build_enhanced_prompt(self, original_task, mcp_results, analysis):
        """构建增强的提示词，整合MCP结果"""
        enhanced_prompt = f"原始任务: {original_task}\n\n"

        if mcp_results:
            enhanced_prompt += "相关信息:\n"
            for i, result in enumerate(mcp_results, 1):
                enhanced_prompt += f"{i}. {result['type']}: {result['content'][:200]}...\n"
            enhanced_prompt += "\n"

        enhanced_prompt += f"任务分析: 类型={analysis['task_type']}, 意图={analysis['intent']}, 复杂度={analysis['complexity']}\n\n"
        enhanced_prompt += "请基于以上信息回答用户的问题:"

        return enhanced_prompt

    def _call_model_with_context(self, model_name, prompt):
        """调用模型并提供上下文"""
        if model_name:
            return self.model_manager.call_model(model_name, prompt)
        else:
            return self.model_manager.call_model('qwen3', prompt)

    def _try_execute_plugin(self, task_description):
        """尝试使用插件执行任务"""
        try:
            # 如果是@查询，直接跳过插件处理
            if task_description.strip().startswith('@'):
                print("🎯 @查询跳过插件处理，直接使用MCP服务")
                return None

            # 检测任务类型并调用相应插件
            task_lower = task_description.lower()

            # Web抓取任务
            if any(keyword in task_lower for keyword in ['网页', '网站', '抓取', '爬取', '分析网页']):
                if 'web_scraper' in [p['name'] for p in self.plugin_manager.list_plugins()]:
                    # 提取URL
                    import re
                    url_match = re.search(r'https?://[^\s]+', task_description)
                    if url_match:
                        url = url_match.group(0)
                        return self.plugin_manager.execute_plugin('web_scraper', action='scrape', url=url)

            # 数据库操作任务
            elif any(keyword in task_lower for keyword in ['数据库', '查询', '插入', '更新', '删除']) and not any(keyword in task_lower for keyword in ['高铁', '火车', '列车', '时刻表', '车次']):
                if 'database' in [p['name'] for p in self.plugin_manager.list_plugins()]:
                    # 解析数据库操作类型
                    if '查询' in task_lower or 'select' in task_lower:
                        action = 'query'
                        # 尝试提取SQL语句或生成简单查询
                        if '用户' in task_lower:
                            sql = "SELECT * FROM users"
                        elif '任务' in task_lower:
                            sql = "SELECT * FROM tasks"
                        else:
                            sql = "SELECT * FROM sqlite_master WHERE type='table'"
                        return self.plugin_manager.execute_plugin('database', action=action, sql=sql)
                    elif '插入' in task_lower or 'insert' in task_lower:
                        action = 'insert'
                        # 这里需要更复杂的解析，暂时返回提示
                        return {"error": "请提供具体的插入数据格式"}
                    elif '更新' in task_lower or 'update' in task_lower:
                        action = 'update'
                        return {"error": "请提供具体的更新条件"}
                    elif '删除' in task_lower or 'delete' in task_lower:
                        action = 'delete'
                        return {"error": "请提供具体的删除条件"}
                    else:
                        # 默认查询所有表
                        return self.plugin_manager.execute_plugin('database', action='query', sql="SELECT name FROM sqlite_master WHERE type='table'")

            # 文件处理任务
            elif any(keyword in task_lower for keyword in ['文件', '读取', '处理', '分析文件']):
                if 'file_processor' in [p['name'] for p in self.plugin_manager.list_plugins()]:
                    return self.plugin_manager.execute_plugin('file_processor', task_description)

            # API调用任务
            elif any(keyword in task_lower for keyword in ['api', '接口', '调用']):
                if 'api_gateway' in [p['name'] for p in self.plugin_manager.list_plugins()]:
                    return self.plugin_manager.execute_plugin('api_gateway', task_description)

            # 通知任务
            elif any(keyword in task_lower for keyword in ['通知', '邮件', '发送']):
                if 'notification' in [p['name'] for p in self.plugin_manager.list_plugins()]:
                    return self.plugin_manager.execute_plugin('notification', task_description)

            return None  # 没有匹配的插件

        except Exception as e:
            logging.error(f"插件执行失败: {e}")
            return None

# 初始化系统
# agent_system = WebAgentSystem()  # 延迟初始化

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
        status = get_agent_system().get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models')
def get_models():
    """获取可用模型列表"""
    try:
        models = get_agent_system().model_manager.get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>')
def get_model_info(model_name):
    """获取特定模型信息"""
    try:
        model_info = get_agent_system().model_manager.get_model_config(model_name)
        if model_info:
            return jsonify(model_info)
        else:
            return jsonify({'error': '模型不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>/test', methods=['POST'])
def test_model(model_name):
    """测试模型功能"""
    try:
        test_result = get_agent_system().model_manager.test_model(model_name)
        return jsonify(test_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_name>/config', methods=['PUT'])
def update_model_config(model_name):
    """更新模型配置"""
    try:
        config = request.get_json()
        success = get_agent_system().model_manager.update_model_config(model_name, config)
        if success:
            return jsonify({'message': '配置更新成功'})
        else:
            return jsonify({'error': '配置更新失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/task', methods=['POST'])
def process_task():
    """处理任务"""
    try:
        data = request.get_json()
        task_description = data.get('task', '')
        model_name = data.get('model', None)

        if not task_description:
            return jsonify({'error': '任务描述不能为空'}), 400

        result = get_agent_system().process_task(task_description, model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """获取任务历史"""
    try:
        limit = int(request.args.get('limit', 20))
        history = get_agent_system().task_history.get_recent_tasks(limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:task_id>')
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        task = get_agent_system().task_history.get_task_by_id(task_id)
        if task:
            return jsonify(task)
        else:
            return jsonify({'error': '任务不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/search')
def search_history():
    """搜索历史记录"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        results = get_agent_system().task_history.search_tasks(query, limit)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/stats')
def get_history_stats():
    """获取历史统计"""
    try:
        days = int(request.args.get('days', 7))
        stats = get_agent_system().task_history.get_task_statistics(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/model/<model_name>')
def get_model_history(model_name):
    """获取指定模型的历史记录"""
    try:
        limit = int(request.args.get('limit', 50))
        history = get_agent_system().task_history.get_tasks_by_model(model_name, limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/export')
def export_history():
    """导出历史记录"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')

        export_data = get_agent_system().task_history.export_tasks(start_date, end_date, format_type)

        if format_type == 'json':
            return Response(export_data, mimetype='application/json')
        elif format_type == 'csv':
            return Response(export_data, mimetype='text/csv')
        else:
            return jsonify({'error': '不支持的导出格式'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/cleanup', methods=['POST'])
def cleanup_history():
    """清理历史记录"""
    try:
        days = int(request.args.get('days', 30))
        deleted_count = get_agent_system().task_history.delete_old_tasks(days)
        return jsonify({'message': f'已删除 {deleted_count} 条历史记录'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins')
def get_plugins():
    """获取插件列表"""
    try:
        plugins = get_agent_system().plugin_manager.list_plugins()
        stats = get_agent_system().plugin_manager.get_plugin_stats()
        return jsonify({'plugins': plugins, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/<plugin_name>')
def get_plugin_info(plugin_name):
    """获取特定插件信息"""
    try:
        plugin_info = get_agent_system().plugin_manager.get_plugin_info(plugin_name)
        if plugin_info:
            return jsonify(plugin_info)
        else:
            return jsonify({'error': '插件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/<plugin_name>/reload', methods=['POST'])
def reload_plugin(plugin_name):
    """重新加载插件"""
    try:
        success = get_agent_system().plugin_manager.reload_plugin(plugin_name)
        if success:
            return jsonify({'message': '插件重新加载成功'})
        else:
            return jsonify({'error': '插件重新加载失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/reload-all', methods=['POST'])
def reload_all_plugins():
    """重新加载所有插件"""
    try:
        results = get_agent_system().plugin_manager.reload_all_plugins()
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/<plugin_name>/validate')
def validate_plugin(plugin_name):
    """验证插件"""
    try:
        validation = get_agent_system().plugin_manager.validate_plugin(plugin_name)
        return jsonify(validation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    """获取性能指标"""
    try:
        metrics = get_agent_system().performance_monitor.get_current_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualize/<chart_type>')
def get_visualization(chart_type):
    """获取可视化数据"""
    try:
        if chart_type == 'performance':
            data = get_agent_system().data_visualizer.generate_performance_chart()
        elif chart_type == 'tasks':
            data = get_agent_system().data_visualizer.generate_task_distribution_chart()
        elif chart_type == 'models':
            data = get_agent_system().data_visualizer.generate_model_usage_chart()
        else:
            return jsonify({'error': '不支持的图表类型'}), 400

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('status', {'message': '已连接到服务器'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_monitoring():
    """开始实时监控"""
    def monitor_loop():
        while True:
            try:
                status = get_agent_system().get_system_status()
                socketio.emit('system_status', status)
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                socketio.emit('error', {'message': str(e)})
                break

    thread = threading.Thread(target=monitor_loop)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    print("🚀 启动多模型智能Agent Web界面...")
    print("📱 Web界面: http://localhost:5000")
    print("🔌 WebSocket: ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
