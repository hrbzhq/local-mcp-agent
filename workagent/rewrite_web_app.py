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
        return {
            'timestamp': datetime.now().isoformat(),
            'models': self.model_manager.get_available_models(),
            'performance': self.performance_monitor.get_current_metrics(),
            'plugins': self.plugin_manager.list_plugins(),
            'tasks': self.task_history.get_recent_tasks(10)
        }

    def process_task(self, task_description, model_name=None):
        """智能处理任务"""
        return {
            'task': task_description,
            'model': model_name,
            'result': '任务已接收，正在处理中...'
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

@app.route('/api/plugins/<plugin_name>')
def get_plugin_info(plugin_name):
    """获取插件信息"""
    try:
        system = get_agent_system()
        plugin_info = system.plugin_manager.get_plugin_info(plugin_name)
        return jsonify(plugin_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/<plugin_name>/reload', methods=['POST'])
def reload_plugin(plugin_name):
    """重新加载插件"""
    try:
        system = get_agent_system()
        success = system.plugin_manager.reload_plugin(plugin_name)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/reload-all', methods=['POST'])
def reload_all_plugins():
    """重新加载所有插件"""
    try:
        system = get_agent_system()
        results = system.plugin_manager.reload_all_plugins()
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins/<plugin_name>/validate', methods=['POST'])
def validate_plugin(plugin_name):
    """验证插件"""
    try:
        system = get_agent_system()
        validation = system.plugin_manager.validate_plugin(plugin_name)
        return jsonify(validation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    print('客户端已连接')

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    print('客户端已断开')

@socketio.on('start_monitoring')
def handle_monitoring():
    """开始实时监控"""
    def monitor_loop():
        while True:
            try:
                system = get_agent_system()
                status = system.get_system_status()
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
