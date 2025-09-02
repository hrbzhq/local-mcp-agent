"""模型管理器，用于调用Ollama模型。

提供 `call_model(model_tag: str, prompt: str, timeout: int=60) -> dict` 和 `list_models()`。

此实现优先使用Ollama CLI；如果不可用，将尝试本地HTTP端点（如果已配置），
否则返回回退响应。
"""
import shlex
import subprocess
import os
import logging
from typing import Dict, Any, List, Union

logger = logging.getLogger(__name__)


def _run_cmd(cmd: str, timeout: int = 60) -> str:
    """运行命令并返回输出。"""
    logger.info(f"执行命令: {cmd}")
    parts = shlex.split(cmd)
    try:
        proc = subprocess.run(parts, capture_output=True, text=True, timeout=timeout)
        out = proc.stdout.strip()
        if proc.returncode != 0:
            logger.warning(f"命令失败 ({proc.returncode}): {proc.stderr.strip()}")
        return out or proc.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"命令超时: {cmd}")
        return "命令执行超时"
    except Exception as e:
        logger.exception(f"命令执行错误: {e}")
        return str(e)


def call_model(model_tag: str, prompt: str, timeout: int = 60) -> Dict[str, Any]:
    """通过Ollama CLI或配置的HTTP端点调用模型。

    参数:
        model_tag: 模型标签
        prompt: 提示词
        timeout: 超时时间（秒）

    返回:
        包含至少以下字段的字典: model, output, raw
    """
    if not model_tag or not prompt:
        return {
            "model": model_tag or "unknown",
            "output": "错误: 模型标签和提示词不能为空",
            "raw": "empty_input_error"
        }

    # 首先尝试CLI
    cli = os.environ.get("OLLAMA_CLI", "ollama")
    cmd = f"{cli} run {shlex.quote(model_tag)} {shlex.quote(prompt)}"
    out = _run_cmd(cmd, timeout=timeout)
    
    # 检查CLI是否成功
    if out and not any(err in out.lower() for err in ["ollama:", "error:", "not found", "命令执行", "超时"]):
        return {
            "model": model_tag,
            "output": out,
            "raw": out,
            "source": "cli"
        }

    # 如果CLI不可用或出错，尝试HTTP端点
    http_url = os.environ.get("OLLAMA_HTTP_URL")
    if http_url:
        try:
            import requests
            endpoint = f"{http_url.rstrip('/')}/api/generate"
            payload = {
                "model": model_tag,
                "prompt": prompt,
                "stream": False
            }
            
            logger.info(f"尝试HTTP调用: {endpoint}")
            resp = requests.post(endpoint, json=payload, timeout=timeout)
            resp.raise_for_status()
            j = resp.json()
            
            return {
                "model": model_tag,
                "output": j.get("response", j.get("output", str(j))),
                "raw": j,
                "source": "http"
            }
        except Exception as e:
            logger.warning(f"HTTP调用Ollama失败: {e}")

    # 最终回退：返回提示信息
    return {
        "model": model_tag,
        "output": f"[回退响应] 模型 {model_tag} 不可用。原始提示: {prompt}",
        "raw": out,
        "source": "fallback"
    }


def list_models() -> Union[List[str], str]:
    """列出可用模型。
    
    返回:
        模型名称列表，或错误时返回错误信息字符串
    """
    cli = os.environ.get("OLLAMA_CLI", "ollama")
    result = _run_cmd(f"{cli} list")
    
    # 尝试解析输出为模型列表
    if result and not any(err in result.lower() for err in ["error:", "not found", "命令执行", "超时"]):
        try:
            lines = result.split('\n')[1:]  # 跳过标题行
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]  # 第一列是模型名
                    if model_name and not model_name.startswith("NAME"):
                        models.append(model_name)
            
            if models:
                return models
        except Exception as e:
            logger.warning(f"解析模型列表失败: {e}")
    
    # 如果CLI失败，尝试HTTP
    http_url = os.environ.get("OLLAMA_HTTP_URL")
    if http_url:
        try:
            import requests
            endpoint = f"{http_url.rstrip('/')}/api/tags"
            resp = requests.get(endpoint, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            
            models = []
            for model in j.get("models", []):
                if "name" in model:
                    models.append(model["name"])
            
            if models:
                return models
        except Exception as e:
            logger.warning(f"HTTP获取模型列表失败: {e}")
    
    # 回退：返回默认模型列表
    logger.info("使用默认模型列表")
    return ["qwen3:8b", "qwen2.5-coder:7b", "qwen2.5vl:3b", "deepseek-r1:latest"]


def get_model_info(model_tag: str) -> Dict[str, Any]:
    """获取模型信息。"""
    cli = os.environ.get("OLLAMA_CLI", "ollama")
    result = _run_cmd(f"{cli} show {shlex.quote(model_tag)}")
    
    return {
        "model": model_tag,
        "available": "error" not in result.lower(),
        "info": result
    }


if __name__ == "__main__":
    print("🔍 测试模型管理器")
    print("可用模型:")
    models = list_models()
    if isinstance(models, list):
        for model in models:
            print(f"  - {model}")
    else:
        print(f"  错误: {models}")
    
    print("\n测试模型调用:")
    result = call_model("qwen3:8b", "你好")
    print(f"  输出: {result.get('output', 'N/A')}")
    print(f"  来源: {result.get('source', 'unknown')}")
    print("✅ 测试完成")
