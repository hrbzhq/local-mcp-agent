"""
系统集成器 - System Integrator for Autonomous Optimization
"""

import os
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import importlib.util

class SystemIntegrator:
    """系统集成器 - 整合所有自主优化组件"""

    def __init__(self):
        self.components = {}  # 已加载的组件
        self.system_status = 'initializing'
        self.component_status = {}
        self.integration_log = []
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'system_integration.json')
        self.load_configuration()

    def load_configuration(self):
        """加载系统配置"""
        default_config = {
            'components': {
                'self_optimization_core': {
                    'path': 'src.self_optimization_core',
                    'class': 'SelfOptimizationCore',
                    'enabled': True,
                    'dependencies': []
                },
                'learning_engine': {
                    'path': 'src.learning_engine',
                    'class': 'LearningEngine',
                    'enabled': True,
                    'dependencies': []
                },
                'decision_maker': {
                    'path': 'src.decision_maker',
                    'class': 'DecisionMaker',
                    'enabled': True,
                    'dependencies': ['learning_engine']
                },
                'resource_manager': {
                    'path': 'src.resource_manager',
                    'class': 'ResourceManager',
                    'enabled': True,
                    'dependencies': []
                },
                'safety_monitor': {
                    'path': 'src.safety_monitor',
                    'class': 'SafetyMonitor',
                    'enabled': True,
                    'dependencies': []
                },
                'mcp_autonomous_optimizer': {
                    'path': 'src.mcp_autonomous_optimizer',
                    'class': 'MCPAutonomousOptimizer',
                    'enabled': True,
                    'dependencies': ['learning_engine', 'decision_maker']
                },
                'capability_boundary_expander': {
                    'path': 'src.capability_boundary_expander',
                    'class': 'CapabilityBoundaryExpander',
                    'enabled': True,
                    'dependencies': []
                },
                'mcp_evolution_optimizer': {
                    'path': 'src.mcp_evolution_optimizer',
                    'class': 'MCPEvolutionOptimizer',
                    'enabled': True,
                    'dependencies': []
                },
                'command_center': {
                    'path': 'src.command_center',
                    'class': 'CommandCenter',
                    'enabled': True,
                    'dependencies': ['learning_engine', 'decision_maker']
                }
            },
            'integration_settings': {
                'auto_start': True,
                'health_check_interval': 30,
                'max_restart_attempts': 3,
                'component_timeout': 60
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置
                    for key, value in loaded_config.items():
                        if key in default_config:
                            if isinstance(value, dict):
                                default_config[key].update(value)
                            else:
                                default_config[key] = value
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")

        self.config = default_config

    def save_configuration(self):
        """保存系统配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")

    def initialize_system(self) -> bool:
        """初始化整个系统"""
        try:
            logging.info("开始系统初始化...")

            # 按依赖顺序加载组件
            load_order = self._calculate_load_order()

            for component_name in load_order:
                if not self._load_component(component_name):
                    logging.error(f"组件 {component_name} 加载失败")
                    return False

            # 建立组件间连接
            self._establish_component_connections()

            # 启动系统服务
            self._start_system_services()

            self.system_status = 'running'
            logging.info("系统初始化完成")
            return True

        except Exception as e:
            logging.error(f"系统初始化失败: {e}")
            self.system_status = 'failed'
            return False

    def _calculate_load_order(self) -> List[str]:
        """计算组件加载顺序"""
        components = self.config['components']
        load_order = []
        loaded = set()
        remaining = set(components.keys())

        while remaining:
            progress = False

            for component_name in list(remaining):
                component_config = components[component_name]

                if not component_config.get('enabled', True):
                    remaining.remove(component_name)
                    continue

                dependencies = component_config.get('dependencies', [])
                if all(dep in loaded for dep in dependencies):
                    load_order.append(component_name)
                    loaded.add(component_name)
                    remaining.remove(component_name)
                    progress = True

            if not progress:
                # 检测循环依赖
                logging.error("检测到组件依赖循环，无法继续加载")
                break

        return load_order

    def _load_component(self, component_name: str) -> bool:
        """加载单个组件"""
        try:
            component_config = self.config['components'][component_name]

            if not component_config.get('enabled', True):
                logging.info(f"组件 {component_name} 已禁用，跳过加载")
                return True

            module_path = component_config['path']
            class_name = component_config['class']

            # 动态导入模块
            module = self._import_module(module_path)
            if not module:
                return False

            # 实例化类
            component_class = getattr(module, class_name, None)
            if not component_class:
                logging.error(f"组件类 {class_name} 在模块 {module_path} 中未找到")
                return False

            # 创建组件实例
            component_instance = component_class()

            # 存储组件
            self.components[component_name] = {
                'instance': component_instance,
                'config': component_config,
                'status': 'loaded',
                'last_health_check': datetime.now(),
                'restart_count': 0
            }

            self.component_status[component_name] = 'loaded'
            logging.info(f"组件 {component_name} 加载成功")
            return True

        except Exception as e:
            logging.error(f"加载组件 {component_name} 失败: {e}")
            self.component_status[component_name] = 'failed'
            return False

    def _import_module(self, module_path: str):
        """动态导入模块"""
        try:
            # 转换为文件路径
            file_path = module_path.replace('.', os.sep) + '.py'
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)

            if not os.path.exists(full_path):
                logging.error(f"模块文件不存在: {full_path}")
                return None

            # 动态导入
            spec = importlib.util.spec_from_file_location(module_path, full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module

        except Exception as e:
            logging.error(f"导入模块 {module_path} 失败: {e}")
            return None

    def _establish_component_connections(self):
        """建立组件间连接"""
        try:
            # 连接学习引擎到决策制定器
            if 'learning_engine' in self.components and 'decision_maker' in self.components:
                decision_maker = self.components['decision_maker']['instance']
                learning_engine = self.components['learning_engine']['instance']
                decision_maker.set_learning_engine(learning_engine)
                logging.info("学习引擎已连接到决策制定器")

            # 连接学习引擎和决策制定器到参谋中心
            if 'command_center' in self.components:
                command_center = self.components['command_center']['instance']

                if 'learning_engine' in self.components:
                    command_center.set_learning_engine(self.components['learning_engine']['instance'])

                if 'decision_maker' in self.components:
                    command_center.set_decision_maker(self.components['decision_maker']['instance'])

                logging.info("学习引擎和决策制定器已连接到参谋中心")

            # 注册模型到参谋中心
            if 'command_center' in self.components:
                self._register_models_to_command_center()

        except Exception as e:
            logging.error(f"建立组件连接失败: {e}")

    def _register_models_to_command_center(self):
        """向参谋中心注册模型"""
        command_center = self.components['command_center']['instance']

        # 注册可用的模型（这里是示例，实际应该从配置或发现机制获取）
        models_to_register = {
            'gpt-4': {
                'capabilities': ['coding', 'analysis', 'generation', 'general'],
                'max_tokens': 8192,
                'provider': 'openai'
            },
            'claude-3': {
                'capabilities': ['analysis', 'writing', 'general'],
                'max_tokens': 4096,
                'provider': 'anthropic'
            },
            'codellama': {
                'capabilities': ['coding', 'debugging'],
                'max_tokens': 2048,
                'provider': 'meta'
            }
        }

        for model_name, model_info in models_to_register.items():
            command_center.register_model(model_name, model_info)

        logging.info(f"已向参谋中心注册 {len(models_to_register)} 个模型")

    def _start_system_services(self):
        """启动系统服务"""
        try:
            # 启动自主优化核心
            if 'self_optimization_core' in self.components:
                optimizer = self.components['self_optimization_core']['instance']
                optimizer.start_optimization()
                logging.info("自主优化核心已启动")

            # 启动资源管理器
            if 'resource_manager' in self.components:
                resource_manager = self.components['resource_manager']['instance']
                resource_manager.start_monitoring()
                logging.info("资源管理器已启动")

            # 启动安全监控器
            if 'safety_monitor' in self.components:
                safety_monitor = self.components['safety_monitor']['instance']
                safety_monitor.start_monitoring()
                logging.info("安全监控器已启动")

            # 启动MCP自主优化器
            if 'mcp_autonomous_optimizer' in self.components:
                mcp_optimizer = self.components['mcp_autonomous_optimizer']['instance']
                mcp_optimizer.start_optimization()
                logging.info("MCP自主优化器已启动")

            # 启动参谋中心
            if 'command_center' in self.components:
                command_center = self.components['command_center']['instance']
                command_center.start_coordination()
                logging.info("参谋中心已启动")

        except Exception as e:
            logging.error(f"启动系统服务失败: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        component_statuses = {}
        for name, component in self.components.items():
            component_statuses[name] = {
                'status': component['status'],
                'last_health_check': component['last_health_check'].isoformat(),
                'restart_count': component['restart_count']
            }

        return {
            'system_status': self.system_status,
            'components': component_statuses,
            'total_components': len(self.components),
            'active_components': len([c for c in self.components.values() if c['status'] == 'running']),
            'timestamp': datetime.now().isoformat()
        }

    def health_check(self):
        """系统健康检查"""
        for component_name, component_data in self.components.items():
            try:
                component_instance = component_data['instance']

                # 检查组件是否有健康检查方法
                if hasattr(component_instance, 'health_check'):
                    health_status = component_instance.health_check()
                    component_data['status'] = 'running' if health_status else 'unhealthy'
                else:
                    # 简单检查：假设组件仍在运行
                    component_data['status'] = 'running'

                component_data['last_health_check'] = datetime.now()

            except Exception as e:
                logging.error(f"组件 {component_name} 健康检查失败: {e}")
                component_data['status'] = 'error'

                # 尝试重启组件
                self._restart_component(component_name)

    def _restart_component(self, component_name: str):
        """重启组件"""
        component_data = self.components[component_name]
        max_attempts = self.config['integration_settings']['max_restart_attempts']

        if component_data['restart_count'] >= max_attempts:
            logging.error(f"组件 {component_name} 重启次数已达上限")
            return

        try:
            logging.info(f"正在重启组件 {component_name}")

            # 停止组件（如果有停止方法）
            component_instance = component_data['instance']
            if hasattr(component_instance, 'stop'):
                component_instance.stop()

            # 重新加载组件
            if self._load_component(component_name):
                component_data['restart_count'] += 1
                component_data['status'] = 'running'
                logging.info(f"组件 {component_name} 重启成功")
            else:
                logging.error(f"组件 {component_name} 重启失败")

        except Exception as e:
            logging.error(f"重启组件 {component_name} 时出错: {e}")

    def shutdown_system(self):
        """关闭整个系统"""
        logging.info("开始系统关闭...")

        # 按相反顺序停止组件
        stop_order = list(self.components.keys())[::-1]

        for component_name in stop_order:
            try:
                component_data = self.components[component_name]
                component_instance = component_data['instance']

                # 调用停止方法（如果存在）
                if hasattr(component_instance, 'stop'):
                    component_instance.stop()
                elif hasattr(component_instance, 'emergency_shutdown'):
                    component_instance.emergency_shutdown()

                component_data['status'] = 'stopped'
                logging.info(f"组件 {component_name} 已停止")

            except Exception as e:
                logging.error(f"停止组件 {component_name} 失败: {e}")

        self.system_status = 'stopped'
        logging.info("系统关闭完成")

    def get_component(self, component_name: str):
        """获取组件实例"""
        if component_name in self.components:
            return self.components[component_name]['instance']
        return None

    def enable_component(self, component_name: str) -> bool:
        """启用组件"""
        if component_name in self.config['components']:
            self.config['components'][component_name]['enabled'] = True
            self.save_configuration()
            logging.info(f"组件 {component_name} 已启用")
            return True
        return False

    def disable_component(self, component_name: str) -> bool:
        """禁用组件"""
        if component_name in self.config['components']:
            self.config['components'][component_name]['enabled'] = False
            self.save_configuration()
            logging.info(f"组件 {component_name} 已禁用")
            return True
        return False

    def start_health_monitoring(self):
        """启动健康监控"""
        def health_monitor_loop():
            while self.system_status == 'running':
                self.health_check()
                time.sleep(self.config['integration_settings']['health_check_interval'])

        health_thread = threading.Thread(target=health_monitor_loop, daemon=True)
        health_thread.start()
        logging.info("健康监控已启动")

    def get_integration_report(self) -> Dict[str, Any]:
        """获取集成报告"""
        return {
            'system_status': self.system_status,
            'components_loaded': len(self.components),
            'components_status': self.component_status,
            'integration_log': self.integration_log[-10:],  # 最近10条日志
            'configuration': self.config,
            'timestamp': datetime.now().isoformat()
        }
