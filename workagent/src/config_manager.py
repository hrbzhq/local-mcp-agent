import json
import os
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

class ConfigManager:
    """配置管理模块"""

    def __init__(self, config_file: str = 'config/settings.json'):
        self.config_file = config_file
        self.config = {}
        self.defaults = {
            # Ollama配置
            'ollama': {
                'base_url': 'http://127.0.0.1:11434',
                'timeout': 30,
                'retry_attempts': 3,
                'retry_delay': 1.0
            },

            # 模型配置
            'models': {
                'qwen3': 'qwen3:0.6b',
                'gemma3': 'gemma3:270m',
                'qwen_coder': 'qwen2.5-coder:0.5b',
                'deepseek_r1': 'deepseek-r1:1.5b',
                'temperature': 0.7,
                'max_tokens': 2048,
                'context_window': 4096
            },

            # MCP配置
            'mcp': {
                'cache_enabled': True,
                'cache_path': 'mcp/mcp_cache.db',
                'remote_search_enabled': True,
                'remote_timeout': 10,
                'auto_update': True
            },

            # 性能配置
            'performance': {
                'monitor_enabled': True,
                'monitor_interval': 1.0,
                'alert_enabled': True,
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'disk_threshold': 90.0
            },

            # 任务配置
            'task': {
                'max_execution_time': 300,  # 5分钟
                'retry_enabled': True,
                'retry_max_attempts': 3,
                'history_enabled': True,
                'history_retention_days': 30
            },

            # 日志配置
            'logging': {
                'level': 'INFO',
                'file_enabled': True,
                'console_enabled': True,
                'max_file_size': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5
            },

            # 系统配置
            'system': {
                'auto_save_interval': 300,  # 5分钟
                'cleanup_interval': 3600,  # 1小时
                'backup_enabled': True,
                'backup_interval': 86400  # 24小时
            }
        }

        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 深度合并配置
                    self.config = self._deep_merge(self.defaults.copy(), loaded_config)
                logging.info(f"配置文件已加载: {self.config_file}")
            else:
                self.config = self.defaults.copy()
                self.save_config()
                logging.info(f"使用默认配置，已创建配置文件: {self.config_file}")
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            self.config = self.defaults.copy()

    def save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info(f"配置文件已保存: {self.config_file}")
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config

        # 创建嵌套结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value
        logging.info(f"配置已更新: {key} = {value}")

        # 自动保存
        self.save_config()

    def reset_to_defaults(self, section: Optional[str] = None):
        """重置为默认配置"""
        if section:
            if section in self.defaults:
                self.config[section] = self.defaults[section].copy()
                logging.info(f"配置段已重置为默认值: {section}")
            else:
                logging.warning(f"未知的配置段: {section}")
        else:
            self.config = self.defaults.copy()
            logging.info("所有配置已重置为默认值")

        self.save_config()

    def validate_config(self) -> Dict[str, Any]:
        """验证配置有效性"""
        issues = []

        # 验证Ollama配置
        ollama_config = self.get('ollama', {})
        if not isinstance(ollama_config.get('timeout'), (int, float)) or ollama_config['timeout'] <= 0:
            issues.append("ollama.timeout 必须是正数")

        # 验证模型配置
        models_config = self.get('models', {})
        required_models = ['qwen3', 'gemma3', 'qwen_coder', 'deepseek_r1']
        for model in required_models:
            if model not in models_config:
                issues.append(f"缺少必需的模型配置: {model}")

        # 验证性能配置
        perf_config = self.get('performance', {})
        if perf_config.get('monitor_interval', 0) <= 0:
            issues.append("performance.monitor_interval 必须是正数")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def export_config(self, file_path: str):
        """导出配置到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info(f"配置已导出到: {file_path}")
        except Exception as e:
            logging.error(f"导出配置失败: {e}")

    def import_config(self, file_path: str):
        """从文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 验证导入的配置
            validation = self.validate_config()
            if not validation['valid']:
                logging.warning(f"导入的配置存在问题: {validation['issues']}")

            self.config = self._deep_merge(self.config, imported_config)
            self.save_config()
            logging.info(f"配置已从 {file_path} 导入")
        except Exception as e:
            logging.error(f"导入配置失败: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            'config_file': self.config_file,
            'last_modified': datetime.fromtimestamp(os.path.getmtime(self.config_file)).isoformat() if os.path.exists(self.config_file) else None,
            'sections': list(self.config.keys()),
            'validation': self.validate_config(),
            'model_count': len(self.get('models', {})),
            'mcp_enabled': self.get('mcp.cache_enabled', False),
            'monitoring_enabled': self.get('performance.monitor_enabled', False),
            'logging_level': self.get('logging.level', 'INFO')
        }

    def create_backup(self) -> str:
        """创建配置备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.config_file}.backup_{timestamp}"

        try:
            self.export_config(backup_file)
            logging.info(f"配置备份已创建: {backup_file}")
            return backup_file
        except Exception as e:
            logging.error(f"创建配置备份失败: {e}")
            return None

    def list_backups(self) -> List[str]:
        """列出所有备份文件"""
        if not os.path.exists(os.path.dirname(self.config_file)):
            return []

        backup_pattern = os.path.basename(self.config_file) + '.backup_'
        backup_dir = os.path.dirname(self.config_file)

        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith(backup_pattern):
                backups.append(os.path.join(backup_dir, file))

        return sorted(backups, reverse=True)

    def restore_backup(self, backup_file: str):
        """从备份恢复配置"""
        if not os.path.exists(backup_file):
            logging.error(f"备份文件不存在: {backup_file}")
            return False

        try:
            # 创建当前配置的备份
            current_backup = self.create_backup()

            # 导入备份配置
            self.import_config(backup_file)
            logging.info(f"配置已从备份恢复: {backup_file}")
            logging.info(f"原配置已备份到: {current_backup}")
            return True
        except Exception as e:
            logging.error(f"恢复配置失败: {e}")
            return False
