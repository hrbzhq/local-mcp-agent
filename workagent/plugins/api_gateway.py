import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.plugin_manager import PluginInterface

class APIGatewayPlugin(PluginInterface):
    """API网关插件"""

    @property
    def name(self) -> str:
        return "api_gateway"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "外部API集成和网关管理插件"

    def __init__(self):
        self.api_configs = {}
        self.request_history = []
        self.rate_limits = {}

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.api_configs = config.get('apis', {})
            self.default_timeout = config.get('default_timeout', 30)
            self.max_retries = config.get('max_retries', 3)
            self.enable_caching = config.get('enable_caching', True)
            self.cache_ttl = config.get('cache_ttl', 300)  # 5分钟

            # 初始化缓存
            self.cache = {}

            logging.info("APIGatewayPlugin 初始化成功")
            return True
        except Exception as e:
            logging.error(f"APIGatewayPlugin 初始化失败: {e}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行API调用"""
        action = kwargs.get('action', 'call')

        if action == 'call':
            return self.call_api(**kwargs)
        elif action == 'batch_call':
            return self.batch_call(**kwargs)
        elif action == 'register_api':
            return self.register_api(**kwargs)
        elif action == 'get_history':
            return self.get_request_history(**kwargs)
        elif action == 'clear_cache':
            return self.clear_cache(**kwargs)
        else:
            return {"error": f"不支持的操作: {action}"}

    def call_api(self, api_name: str, endpoint: str = '', method: str = 'GET',
                 params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """调用外部API"""
        try:
            if api_name not in self.api_configs:
                return {"error": f"未注册的API: {api_name}"}

            api_config = self.api_configs[api_name]
            base_url = api_config.get('base_url', '')

            # 构造完整URL
            url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')

            # 检查缓存
            cache_key = f"{method}:{url}:{json.dumps(params, sort_keys=True) if params else ''}"
            if self.enable_caching and method.upper() == 'GET':
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    return cached_result

            # 检查速率限制
            if not self._check_rate_limit(api_name):
                return {"error": f"API {api_name} 达到速率限制"}

            # 准备请求
            request_config = {
                'method': method.upper(),
                'url': url,
                'timeout': api_config.get('timeout', self.default_timeout),
                'headers': headers or api_config.get('headers', {})
            }

            if params:
                request_config['params'] = params
            if data:
                if isinstance(data, dict):
                    request_config['json'] = data
                else:
                    request_config['data'] = data

            # 添加认证
            if 'auth' in api_config:
                auth_config = api_config['auth']
                if auth_config.get('type') == 'bearer':
                    request_config['headers']['Authorization'] = f"Bearer {auth_config['token']}"
                elif auth_config.get('type') == 'basic':
                    request_config['auth'] = (auth_config['username'], auth_config['password'])

            # 发送请求（带重试）
            response = None
            last_error = None

            for attempt in range(self.max_retries):
                try:
                    response = requests.request(**request_config)
                    break
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                    continue

            if response is None:
                return {"error": f"请求失败: {str(last_error)}"}

            # 解析响应
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_data = response.json()
                else:
                    response_data = response.text
            except Exception as e:
                logging.debug(f"解析响应为JSON失败，使用纯文本响应: {e}")
                response_data = response.text

            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "url": url,
                "method": method,
                "timestamp": datetime.now().isoformat()
            }

            # 记录请求历史
            self._record_request(api_name, result)

            # 缓存成功响应
            if self.enable_caching and method.upper() == 'GET' and response.status_code < 400:
                self._set_cache(cache_key, result)

            return result

        except Exception as e:
            logging.error(f"API调用失败 {api_name}: {e}")
            return {"error": str(e)}

    def batch_call(self, calls: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """批量调用API"""
        try:
            results = []
            for call_config in calls:
                result = self.call_api(**call_config)
                results.append(result)

                # 如果需要顺序执行，可以在这里添加延迟
                if kwargs.get('sequential', False):
                    time.sleep(kwargs.get('delay', 0.1))

            return {
                "status": "completed",
                "total_calls": len(calls),
                "successful_calls": sum(1 for r in results if 'error' not in r),
                "results": results
            }

        except Exception as e:
            logging.error(f"批量API调用失败: {e}")
            return {"error": str(e)}

    def register_api(self, name: str, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """注册新的API配置"""
        try:
            required_fields = ['base_url']
            for field in required_fields:
                if field not in config:
                    return {"error": f"缺少必需字段: {field}"}

            self.api_configs[name] = config

            return {
                "status": "success",
                "api_name": name,
                "config": config
            }

        except Exception as e:
            logging.error(f"注册API失败: {e}")
            return {"error": str(e)}

    def get_request_history(self, api_name: Optional[str] = None, limit: int = 50, **kwargs) -> Dict[str, Any]:
        """获取请求历史"""
        try:
            history = self.request_history

            if api_name:
                history = [h for h in history if h.get('api_name') == api_name]

            history = history[-limit:] if limit > 0 else history

            return {
                "status": "success",
                "api_name": api_name,
                "total_count": len(self.request_history),
                "returned_count": len(history),
                "history": history
            }

        except Exception as e:
            logging.error(f"获取请求历史失败: {e}")
            return {"error": str(e)}

    def clear_cache(self, **kwargs) -> Dict[str, Any]:
        """清空缓存"""
        try:
            cache_count = len(self.cache)
            self.cache.clear()

            return {
                "status": "success",
                "cleared_entries": cache_count
            }

        except Exception as e:
            logging.error(f"清空缓存失败: {e}")
            return {"error": str(e)}

    def _check_rate_limit(self, api_name: str) -> bool:
        """检查速率限制"""
        if api_name not in self.api_configs:
            return True

        api_config = self.api_configs[api_name]
        rate_limit = api_config.get('rate_limit', {})

        if not rate_limit:
            return True

        limit = rate_limit.get('requests', 60)
        window = rate_limit.get('window', 60)  # 秒

        now = datetime.now()
        key = f"{api_name}_requests"

        if key not in self.rate_limits:
            self.rate_limits[key] = []

        # 清理过期的请求记录
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key]
            if (now - req_time).seconds < window
        ]

        # 检查是否超过限制
        if len(self.rate_limits[key]) >= limit:
            return False

        # 记录当前请求
        self.rate_limits[key].append(now)
        return True

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if key in self.cache:
            entry = self.cache[key]
            if (datetime.now() - entry['timestamp']).seconds < self.cache_ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]):
        """设置缓存"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def _record_request(self, api_name: str, result: Dict[str, Any]):
        """记录请求历史"""
        record = {
            'api_name': api_name,
            'timestamp': datetime.now().isoformat(),
            'method': result.get('method'),
            'url': result.get('url'),
            'status_code': result.get('status_code'),
            'success': result.get('status_code', 500) < 400
        }

        self.request_history.append(record)

        # 只保留最近1000条记录
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def cleanup(self):
        """清理资源"""
        self.cache.clear()
        self.request_history.clear()
        self.rate_limits.clear()
        logging.info("APIGatewayPlugin 清理完成")
