"""简单的多模型网关路由器。

提供 `select_model(text: str, user_model: Optional[str]=None) -> str` 供 `api_server.py` 使用。

这个文件设计为小而基于规则。在生产环境中，可以用基于嵌入的路由或可配置的规则引擎替换。
"""
from typing import Optional
import os
import yaml


def _load_config(config_path: str = "config.yaml") -> dict:
    """加载YAML配置文件。"""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}")
            return {}
    return {}


# 默认模型映射
_DEFAULT_MAP = {
    "code": "qwen2.5-coder:7b",
    "image": "qwen2.5vl:3b", 
    "long": "qwen3:8b",
    "fast": "gemma3:latest",
    "reasoning": "deepseek-r1:latest",
    "general": "qwen3:8b"
}

# 加载配置
_CFG = _load_config()


def select_model(text: str, user_model: Optional[str] = None) -> str:
    """根据输入文本或显式的用户模型选择模型标签。

    参数:
      - text: 用户提示词
      - user_model: 可选的显式模型标签

    返回:
      - Ollama 模型标签 (字符串)
    """
    if user_model:
        return user_model

    t = (text or "").lower()

    # 使用基于配置的路由（如果可用）
    routing = _CFG.get("routing", {})
    defaults = _CFG.get("defaults", _DEFAULT_MAP)

    # 检查代码相关关键词
    code_keywords = routing.get("code_keywords", [
        "代码", "编程", "函数", "爬虫", "debug", "python", "java", "js", 
        "javascript", "code", "programming", "script", "算法", "开发"
    ])
    if any(k in t for k in code_keywords):
        return defaults.get("code", _DEFAULT_MAP["code"])

    # 检查视觉相关关键词
    vision_keywords = routing.get("vision_keywords", [
        "图片", "图像", "看图", "视觉", "image", "photo", "picture", "截图", "画面"
    ])
    if any(k in t for k in vision_keywords):
        return defaults.get("image", _DEFAULT_MAP["image"])

    # 检查推理相关关键词
    reasoning_keywords = routing.get("reasoning_keywords", [
        "分析", "推理", "思考", "解释", "为什么", "如何", "reasoning", 
        "analyze", "深度", "复杂", "逻辑", "推导"
    ])
    if any(k in t for k in reasoning_keywords):
        return defaults.get("reasoning", _DEFAULT_MAP["reasoning"])

    # 检查快速/简单关键词
    fast_keywords = routing.get("fast_keywords", [
        "快速", "简单", "摘要", "总结", "brief", "quick", "简短", "概括"
    ])
    if any(k in t for k in fast_keywords):
        return defaults.get("fast", _DEFAULT_MAP["fast"])

    # 检查长文本处理关键词
    long_keywords = routing.get("long_keywords", [
        "长文", "详细", "全面", "深入", "comprehensive", "detailed", "论文", "报告"
    ])
    if any(k in t for k in long_keywords):
        return defaults.get("long", _DEFAULT_MAP["long"])

    # 回退：使用配置的默认值，否则使用通用模型
    return defaults.get("general", _DEFAULT_MAP["general"])


if __name__ == "__main__":
    # 快速本地测试
    examples = [
        "帮我写一个Python爬虫",
        "这张图片里有什么？", 
        "写一篇关于 LLM 的详细综述，3000 字",
        "给我一个简短摘要",
        "深度分析这个问题的逻辑",
        "快速总结一下要点"
    ]
    print("🔍 模型路由测试:")
    for e in examples:
        model = select_model(e)
        print(f"  '{e}' -> {model}")
    print("✅ 路由测试完成")
