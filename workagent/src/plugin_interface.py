from abc import ABC, abstractmethod
from typing import Dict, Any

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
