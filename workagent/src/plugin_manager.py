import importlib
import inspect
import os
import sys
from typing import Dict, List, Any, Optional, Callable
import logging
from abc import ABC, abstractmethod
from datetime import datetime


class PluginInterface(ABC):
    """插件接口基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """执行插件功能"""
        pass

    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass


class PluginManager:
    """插件管理器"""

    def __init__(self, plugin_dir: str = 'plugins'):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.loaded_plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}

        # 创建插件目录
        os.makedirs(plugin_dir, exist_ok=True)

    def discover_plugins(self) -> List[str]:
        """发现可用的插件"""
        plugins = []

        if not os.path.exists(self.plugin_dir):
            return plugins

        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)

            # 检查是否是Python文件或包
            if item.endswith('.py') and item != '__init__.py':
                plugin_name = item[:-3]  # 移除.py扩展名
                plugins.append(plugin_name)
            elif os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                plugins.append(item)

        return plugins

    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """加载插件"""
        try:
            # 构造模块路径 - 直接导入插件文件
            # plugin_file 变量仅用于存在性检查 in other methods; 不在此处使用

            # 确保插件目录在Python路径中
            if self.plugin_dir not in sys.path:
                sys.path.insert(0, self.plugin_dir)

            # 直接导入模块
            module = importlib.import_module(plugin_name)

            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                logging.debug(f"检查成员: {name} = {obj}")
                if inspect.isclass(obj):
                    logging.debug(f"  是类: {obj}")
                    logging.debug(f"  PluginInterface: {PluginInterface}")
                    logging.debug(f"  issubclass(obj, PluginInterface): {issubclass(obj, PluginInterface)}")
                    logging.debug(f"  obj != PluginInterface: {obj != PluginInterface}")
                    if (issubclass(obj, PluginInterface)
                            and obj != PluginInterface):
                        plugin_class = obj
                        logging.info(f"找到插件类: {name}")
                        break

            if not plugin_class:
                logging.error(f"插件 {plugin_name} 中未找到有效的插件类")
                # 调试信息
                logging.error(f"模块成员: {list(inspect.getmembers(module))}")
                return False

            # 实例化插件
            plugin_instance = plugin_class()

            # 初始化插件
            if config is None:
                config = {}

            if not plugin_instance.initialize(config):
                logging.error(f"插件 {plugin_name} 初始化失败")
                return False

            # 注册插件
            self.plugins[plugin_name] = plugin_instance
            self.loaded_plugins[plugin_name] = module

            logging.info(f"插件 {plugin_name} (v{plugin_instance.version}) 已加载")
            return True

        except Exception as e:
            logging.error(f"加载插件 {plugin_name} 失败: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name not in self.plugins:
            logging.warning(f"插件 {plugin_name} 未加载")
            return False

        try:
            # 清理插件资源
            self.plugins[plugin_name].cleanup()

            # 从注册表中移除
            del self.plugins[plugin_name]
            del self.loaded_plugins[plugin_name]

            logging.info(f"插件 {plugin_name} 已卸载")
            return True

        except Exception as e:
            logging.error(f"卸载插件 {plugin_name} 失败: {e}")
            return False

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """执行插件"""
        if plugin_name not in self.plugins:
            raise ValueError(f"插件 {plugin_name} 未加载")

        try:
            return self.plugins[plugin_name].execute(*args, **kwargs)
        except Exception as e:
            logging.error(f"执行插件 {plugin_name} 失败: {e}")
            raise

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件信息"""
        if plugin_name not in self.plugins:
            return None

        plugin = self.plugins[plugin_name]
        return {
            'name': plugin.name,
            'version': plugin.version,
            'description': plugin.description,
            'loaded': True,
            'status': 'active',
            'last_used': getattr(plugin, 'last_used', None),
            'usage_count': getattr(plugin, 'usage_count', 0)
        }

    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有已加载的插件"""
        plugin_list = []
        for name, plugin in self.plugins.items():
            plugin_list.append({
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'loaded': True,
                'status': 'active',
                'last_used': getattr(plugin, 'last_used', None),
                'usage_count': getattr(plugin, 'usage_count', 0)
            })
        return plugin_list

    def get_plugin_stats(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        total_plugins = len(self.plugins)
        loaded_plugins = len([p for p in self.plugins.values() if hasattr(p, 'usage_count')])

        return {
            'total_plugins': total_plugins,
            'loaded_plugins': loaded_plugins,
            'available_plugins': len(self.discover_plugins()),
            'plugin_usage': {name: getattr(plugin, 'usage_count', 0) for name, plugin in self.plugins.items()}
        }

    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        try:
            # 先卸载
            if not self.unload_plugin(plugin_name):
                return False

            # 再加载
            return self.load_plugin(plugin_name)

        except Exception as e:
            logging.error(f"重新加载插件 {plugin_name} 失败: {e}")
            return False

    def reload_all_plugins(self) -> Dict[str, bool]:
        """重新加载所有插件"""
        results = {}
        plugin_names = list(self.plugins.keys())

        for plugin_name in plugin_names:
            results[plugin_name] = self.reload_plugin(plugin_name)

        return results

    def get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """获取插件依赖"""
        if plugin_name not in self.plugins:
            return []

        plugin = self.plugins[plugin_name]
        return getattr(plugin, 'dependencies', [])

    def validate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """验证插件完整性"""
        validation_result = {
            'valid': False,
            'errors': [],
            'warnings': []
        }

        if plugin_name not in self.plugins:
            validation_result['errors'].append(f"插件 {plugin_name} 未加载")
            return validation_result

        plugin = self.plugins[plugin_name]

        # 检查必需属性
        required_attrs = ['name', 'version', 'description']
        for attr in required_attrs:
            if not hasattr(plugin, attr):
                validation_result['errors'].append(f"缺少必需属性: {attr}")

        # 检查必需方法
        required_methods = ['initialize', 'execute', 'cleanup']
        for method in required_methods:
            if not hasattr(plugin, method):
                validation_result['errors'].append(f"缺少必需方法: {method}")

        # 检查依赖
        dependencies = self.get_plugin_dependencies(plugin_name)
        for dep in dependencies:
            if dep not in self.plugins:
                validation_result['warnings'].append(f"依赖插件未加载: {dep}")

        validation_result['valid'] = len(validation_result['errors']) == 0
        return validation_result

    def get_plugin_logs(self, plugin_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取插件执行日志"""
        # 这里可以实现插件日志记录功能
        # 暂时返回空列表
        return []

    def export_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """导出插件配置"""
        if plugin_name not in self.plugins:
            return None

        plugin = self.plugins[plugin_name]
        return {
            'name': plugin.name,
            'version': plugin.version,
            'description': plugin.description,
            'config': getattr(plugin, 'config', {}),
            'exported_at': str(datetime.now())
        }

    def import_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """导入插件配置"""
        try:
            if plugin_name not in self.plugins:
                return False

            plugin = self.plugins[plugin_name]
            if hasattr(plugin, 'load_config'):
                plugin.load_config(config)
                return True
            else:
                # 直接设置配置
                plugin.config = config
                return True

        except Exception as e:
            logging.error(f"导入插件 {plugin_name} 配置失败: {e}")
            return False

    def register_hook(self, hook_name: str, callback: Callable):
        """注册钩子"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
        logging.info(f"钩子已注册: {hook_name}")

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """触发钩子"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f"执行钩子 {hook_name} 失败: {e}")

    def create_plugin_template(self, plugin_name: str, plugin_type: str = 'basic') -> str:
        """创建插件模板"""
        template_dir = os.path.join(self.plugin_dir, plugin_name)
        os.makedirs(template_dir, exist_ok=True)

        # 创建__init__.py
        init_content = f'''"""
{plugin_name} 插件
"""

from .{plugin_name} import {plugin_name.title()}Plugin

__version__ = "1.0.0"
'''

        # 创建插件主文件
        plugin_content = f'''"""
{plugin_name} 插件实现
"""

from ..plugin_interface import PluginInterface
from typing import Dict, Any

class {plugin_name.title()}Plugin(PluginInterface):
    """{plugin_name} 插件"""

    @property
    def name(self) -> str:
        return "{plugin_name}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "{plugin_name} 插件描述"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            # 在这里初始化插件
            print(f"初始化插件: {{self.name}}")
            return True
        except Exception as e:
            print(f"插件初始化失败: {{e}}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行插件功能"""
        # 在这里实现插件的主要功能
        print(f"执行插件: {{self.name}}")
        return f"插件 {{self.name}} 执行结果"

    def cleanup(self):
        """清理插件资源"""
        print(f"清理插件: {{self.name}}")
'''

        # 写入文件
        with open(os.path.join(template_dir, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write(init_content)

        with open(os.path.join(template_dir, f'{plugin_name}.py'), 'w', encoding='utf-8') as f:
            f.write(plugin_content)

        logging.info(f"插件模板已创建: {template_dir}")
        return template_dir

    # ...existing code...
