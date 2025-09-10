import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional
from .capability_learner import CapabilityLearner


class ModelManager:
    def __init__(self):
        # 配置ollama API端点
        self.ollama_host = 'http://localhost:11434'
        self.api_url = f"{self.ollama_host}/api/generate"
        # Ollama model listing endpoint can vary; use a common /api/models path
        # and tolerate different response shapes in the status checker.
        self.list_url = f"{self.ollama_host}/api/models"

        # 配置模型，添加错误处理
        self.models = {}
        self.model_status = {}
        self.model_configs = {}
        self.init_models()

    def init_models(self):
        """初始化模型，带错误处理"""
        model_configs = {
            'qwen3': {
                'name': 'qwen3:0.6b',
                'description': '通义千问3模型，适合中文对话',
                'size': '0.6B',
                'capabilities': ['text_generation', 'code_generation', 'analysis'],
                'temperature': 0.7,
                'max_tokens': 2048
            },
            'gemma3': {
                'name': 'gemma3:270m',
                'description': 'Google Gemma3模型，轻量快速',
                'size': '270M',
                'capabilities': ['text_generation', 'quick_response'],
                'temperature': 0.8,
                'max_tokens': 1024
            },
            'qwen_coder': {
                'name': 'qwen2.5-coder:0.5b',
                'description': '通义千问Coder，编程专用',
                'size': '0.5B',
                'capabilities': ['code_generation', 'debugging', 'code_review'],
                'temperature': 0.3,
                'max_tokens': 2048
            },
            'deepseek_r1': {
                'name': 'deepseek-r1:1.5b',
                'description': 'DeepSeek R1推理模型',
                'size': '1.5B',
                'capabilities': ['reasoning', 'analysis', 'optimization'],
                'temperature': 0.6,
                'max_tokens': 4096
            }
        }

        for key, config in model_configs.items():
            try:
                self.models[key] = config['name']
                self.model_configs[key] = config
                self.model_status[key] = 'unknown'
                logging.info("模型 %s (%s) 配置成功", key, config['name'])
            except Exception as e:
                logging.error("模型 %s (%s) 配置失败: %s", key, config['name'], e)
                self.models[key] = None
                self.model_status[key] = 'error'

    def check_model_status(self, model_name: str) -> str:
        """检查模型状态"""
        try:
            model = self.models.get(model_name)
            if model is None:
                return 'unavailable'

            # 首先检查模型是否在已安装的模型列表中
            try:
                list_response = requests.get(self.list_url, timeout=5)
                if list_response.status_code == 200:
                    models_data = list_response.json()
                    # Handle different possible shapes returned by Ollama/local APIs
                    installed_models = []
                    if isinstance(models_data, dict):
                        # Common shape: { 'models': [ { 'name': '...' }, ... ] }
                        for m in models_data.get('models', []):
                            if isinstance(m, dict):
                                name = m.get('name')
                                if name:
                                    installed_models.append(name)
                            elif isinstance(m, str):
                                installed_models.append(m)
                    elif isinstance(models_data, list):
                        # Some endpoints return a flat list
                        for m in models_data:
                            if isinstance(m, dict):
                                name = m.get('name')
                                if name:
                                    installed_models.append(name)
                            elif isinstance(m, str):
                                installed_models.append(m)

                    if installed_models and model not in installed_models:
                        return 'offline'
            except Exception as e:
                logging.warning("无法获取已安装模型列表: %s", e)

            # 尝试调用模型进行简单测试
            payload = {
                "model": model,
                "prompt": "test",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 10
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                return 'online'
            else:
                return 'offline'

        except requests.exceptions.Timeout:
            logging.error("检查模型 %s 状态超时", model_name)
            return 'offline'
        except Exception as e:
            logging.error("检查模型 %s 状态失败: %s", model_name, e)
            return 'error'

    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取所有可用模型的详细信息"""
        models_info = []

        for key, config in self.model_configs.items():
            status = self.check_model_status(key)
            self.model_status[key] = status

            model_info = {
                'id': key,
                'name': config['name'],
                'display_name': key.replace('_', ' ').title(),
                'description': config['description'],
                'size': config['size'],
                'capabilities': config['capabilities'],
                'status': status,
                'temperature': config['temperature'],
                'max_tokens': config['max_tokens']
            }
            models_info.append(model_info)

        return models_info

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取模型配置"""
        return self.model_configs.get(model_name)

    def update_model_config(self, model_name: str, config: Dict[str, Any]) -> bool:
        """更新模型配置"""
        try:
            if model_name not in self.model_configs:
                return False

            # 更新配置
            self.model_configs[model_name].update(config)
            logging.info("模型 %s 配置已更新", model_name)
            return True

        except Exception as e:
            logging.error("更新模型 %s 配置失败: %s", model_name, e)
            return False

    def get_model(self, model_name: str) -> Optional[str]:
        """获取模型，带状态检查"""
        model = self.models.get(model_name)
        if model is None:
            logging.warning("模型 %s 未初始化", model_name)
        return model

    def call_model(self, model_name: str, prompt: str) -> str:
        """调用模型，带错误处理"""
        try:
            model = self.get_model(model_name)
            if model is None:
                return "模型 %s 不可用" % model_name

            logging.info("调用模型 %s 处理提示: %s...", model_name, prompt[:50])

            # 获取模型配置
            config = self.get_model_config(model_name) or {}
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2048)

            # 使用requests直接调用Ollama API
            payload = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_ctx": max_tokens
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60  # 增加超时时间
            )

            if response.status_code == 200:
                # Ollama返回的是流式响应，需要处理
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue

                if full_response:
                    logging.info("模型 %s 响应成功", model_name)
                    return full_response
                else:
                    logging.warning("模型 %s 返回空响应", model_name)
                    return "模型返回空响应"
            else:
                logging.error("模型 %s API调用失败: HTTP %s", model_name, response.status_code)
                return "模型调用失败: HTTP %s" % response.status_code

        except requests.exceptions.Timeout:
            logging.error("模型 %s 调用超时", model_name)
            return "模型连接失败: 请求超时"
        except requests.exceptions.ConnectionError as e:
            logging.error("模型 %s 连接失败: %s", model_name, e)
            return "模型连接失败: 网络连接问题"
        except Exception as e:
            logging.error("模型 %s 调用失败: %s", model_name, e)
            return "模型调用失败: %s" % e

    def test_model(
        self,
        model_name: str,
        test_prompt: str = (
            "Hello, please respond with 'OK' if you can understand this message."
        ),
    ) -> Dict[str, Any]:
        """测试模型功能"""
        start_time = time.time()

        try:
            response = self.call_model(model_name, test_prompt)
            execution_time = time.time() - start_time

            # Normalize response to string and decide success by absence of known error prefixes
            resp_text = str(response or "")
            success = not resp_text.startswith("模型") and not resp_text.lower().startswith('error')

            return {
                'model': model_name,
                'success': success,
                'response': response,
                'execution_time': execution_time,
                'status': 'online' if success else 'error'
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logging.error("测试模型 %s 时出现异常: %s", model_name, e)
            return {
                'model': model_name,
                'success': False,
                'response': str(e),
                'execution_time': execution_time,
                'status': 'error'
            }

    def test_models(self):
        """测试所有模型连接"""
        results = {}
        for name in self.models.keys():
            try:
                response = self.call_model(name, "Hello, test message")
                # 检查响应是否包含错误信息
                if "失败" in str(response) or "错误" in str(response) or "不可用" in str(response):
                    results[name] = "失败"
                else:
                    results[name] = "成功"
            except Exception as e:
                logging.warning("测试模型 %s 失败: %s", name, e)
                results[name] = "失败"
        return results

    def discover_and_attempt(self, query: str) -> Dict[str, Any]:
        """Use MCP to discover a missing capability and attempt a safe simulation.

        Returns a summary: raw MCP text, extracted code (if any), safety analysis,
        and a simulated execution result or review recommendation.
        """
        learner = CapabilityLearner()
        return learner.simulate_execute(query)
