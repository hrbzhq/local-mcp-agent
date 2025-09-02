from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import time
import subprocess
import shlex
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Local Multi-Model AI Gateway",
    description="A unified API gateway for multiple local AI models with MCP support",
    version="2.0.0"
)


# 根路径，重定向到文档，便于浏览器访问
@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root requests to the interactive docs for easy browsing."""
    return RedirectResponse(url="/docs")

# Import authentication module
try:
    from auth import (
        auth_middleware, require_auth, optional_auth, is_auth_enabled,
        get_auth_status, generate_api_key, get_api_key
    )
    logger.info("✅ 认证模块加载成功")
    # Add authentication middleware
    app.middleware("http")(auth_middleware)
    # Set auth dependencies as app attributes for MCP integration
    app.require_auth = require_auth
    app.optional_auth = optional_auth
except ImportError as e:
    logger.warning(f"❌ 认证模块不可用: {e}")
    # Fallback functions
    def require_auth(): return None
    def optional_auth(): return None
    def is_auth_enabled(): return False
    def get_auth_status(): return {"auth_enabled": False}
    def generate_api_key(): return "demo-key"
    # Set fallback auth dependencies
    app.require_auth = require_auth
    app.optional_auth = optional_auth

# Import MCP integration
try:
    from mcp_server import mcp_server, integrate_with_fastapi
    logger.info("✅ MCP集成加载成功")
    # Integrate MCP routes with FastAPI
    integrate_with_fastapi(app)
except ImportError as e:
    logger.warning(f"❌ MCP集成不可用: {e}")
    mcp_server = None


class ChatRequest(BaseModel):
    input: str
    user_id: Optional[str] = "anonymous"
    model: Optional[str] = None
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    model: str
    output: str
    user_id: str
    meta: Dict[str, Any]


class MCPRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    tools: Optional[List[Dict[str, Any]]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Global fallback implementations
def _run_cmd(cmd: str, timeout: int = 60) -> str:
    """运行shell命令并返回stdout（解码后）。"""
    logger.info(f"执行命令: {cmd}")
    parts = shlex.split(cmd)
    try:
        proc = subprocess.run(parts, capture_output=True, text=True, timeout=timeout)
        out = proc.stdout.strip()
        if proc.returncode != 0:
            logger.warning(f"命令退出码 {proc.returncode}, stderr: {proc.stderr.strip()}")
        return out or proc.stderr.strip()
    except Exception as e:
        logger.exception(f"命令执行失败: {e}")
        return str(e)


def _fallback_call_model(model_tag: str, prompt: str, timeout: int = 60) -> Dict[str, Any]:
    """通过CLI调用Ollama模型。如果Ollama未安装，返回回退响应。"""
    cmd = f"ollama run {shlex.quote(model_tag)} --prompt {shlex.quote(prompt)}"
    out = _run_cmd(cmd, timeout=timeout)
    if out.lower().startswith("ollama:") or "not found" in out.lower():
        # Ollama不可用；返回占位符响应
        return {"model": model_tag, "output": f"[回退响应] {prompt}", "raw": out}
    return {"model": model_tag, "output": out, "raw": out}


def _fallback_list_models() -> List[str]:
    """获取可用模型列表的回退实现。"""
    try:
        result = _run_cmd("ollama list")
        # 解析ollama list输出，提取模型名称
        lines = result.split('\n')[1:]  # 跳过标题行
        models = []
        for line in lines:
            if line.strip():
                model_name = line.split()[0]  # 第一列是模型名
                models.append(model_name)
        return models if models else ["qwen3:8b"]  # 默认模型
    except Exception as e:
        logger.warning(f"获取模型列表失败: {e}")
        return ["qwen3:8b"]  # 返回默认模型


def _fallback_select_model(request_text: str) -> str:
    """基于关键词的简单模型路由（在router.py中扩展）。"""
    text = request_text.lower()
    if any(k in text for k in ("代码", "编程", "函数", "爬虫", "python", "java", "js", "javascript", "code", "programming")):
        return "qwen2.5-coder:7b"
    if any(k in text for k in ("图片", "图像", "看图", "视觉", "image", "photo", "vision")):
        return "qwen2.5vl:3b"
    if any(k in text for k in ("分析", "推理", "思考", "reasoning", "analysis", "deepseek")):
        return "deepseek-r1:latest"
    # 默认高质量对话模型
    return "qwen3:8b"


# Try to import pluggable modules; if not present use simple fallbacks
try:
    from router import select_model  # type: ignore
    from model_manager import call_model, list_models  # type: ignore
    logger.info("✅ 加载外部路由/模型管理模块")
except Exception as e:
    logger.warning(f"⚠️  使用内置回退路由和模型管理器: {e}")
    # Use fallback implementations
    select_model = _fallback_select_model
    call_model = _fallback_call_model
    list_models = _fallback_list_models


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user: Optional[str] = optional_auth()):
    """通过网关与AI模型聊天。"""
    if not req.input or not req.input.strip():
        raise HTTPException(status_code=400, detail="需要输入内容")

    start = time.time()

    # 如果未指定模型则自动选择
    model_tag = req.model or select_model(req.input)

    call_start = time.time()
    result = call_model(model_tag, req.input)
    call_end = time.time()

    latency_ms = int((time.time() - start) * 1000)
    output = result.get("output") if isinstance(result, dict) else str(result)

    meta = {
        "latency_ms": latency_ms,
        "model_call_ms": int((call_end - call_start) * 1000),
        "model_selected": "auto" if not req.model else "manual",
        "input_length": len(req.input),
        "output_length": len(output),
        "timestamp": time.time(),
        "authenticated": user is not None
    }

    return ChatResponse(
        model=model_tag,
        output=output,
        user_id=req.user_id,
        meta=meta
    )


@app.get("/models")
def get_models():
    """获取可用模型列表。"""
    try:
        models_list = list_models()
        return {
            "models": models_list,
            "count": len(models_list) if isinstance(models_list, list) else 1,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.exception("获取模型列表失败")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@app.get("/health")
def health():
    """基础健康检查，包含认证状态。"""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "version": "2.0.0",
        "auth_enabled": is_auth_enabled(),
        "mcp_enabled": mcp_server is not None
    }


@app.get("/stats")
def get_stats():
    """获取服务器统计信息。"""
    stats = {
        "server": {
            "status": "运行中",
            "version": "2.0.0",
            "uptime": time.time()
        },
        "features": {
            "auth_enabled": is_auth_enabled(),
            "mcp_enabled": mcp_server is not None
        },
        "timestamp": time.time()
    }
    
    # 如果MCP服务器可用，添加MCP统计信息
    if mcp_server:
        try:
            mcp_stats = mcp_server.get_stats()
            stats["mcp"] = mcp_stats
        except Exception as e:
            logger.warning(f"获取MCP统计信息失败: {e}")
    
    return stats


# Enhanced MCP Integration
@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest, user: Optional[str] = require_auth()):
    """增强的MCP协议端点，支持认证。"""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP服务器不可用")

    try:
        method = request.method
        params = request.params or {}

        if method == "tools/list":
            tools = await mcp_server.list_tools()
            return MCPResponse(tools=tools)

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = await mcp_server.call_tool(tool_name, tool_args)
            return MCPResponse(result=result)

        else:
            return MCPResponse(error=f"未知方法: {method}")

    except Exception as e:
        logger.exception(f"MCP请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"MCP请求失败: {str(e)}")


@app.get("/auth/status")
def get_authentication_status():
    """获取认证状态和配置。"""
    return get_auth_status()


@app.post("/auth/generate-key")
def generate_new_api_key():
    """生成新的API密钥（仅用于开发/测试）。"""
    if is_auth_enabled():
        # 在生产环境中，这应该受到保护，仅对管理员可用
        return {
            "warning": "认证已启用。此端点仅用于开发。",
            "generated_key": generate_api_key(),
            "env_var": "GATEWAY_API_KEY",
            "header": "X-API-Key"
        }
    else:
        return {
            "generated_key": generate_api_key(),
            "env_var": "GATEWAY_API_KEY",
            "header": "X-API-Key",
            "instructions": "设置GATEWAY_API_KEY环境变量以启用认证"
        }


@app.get("/auth/test")
def test_authentication(user: Optional[str] = optional_auth()):
    """测试认证状态。"""
    return {
        "authenticated": user is not None,
        "user": user,
        "auth_enabled": is_auth_enabled(),
        "timestamp": time.time()
    }


@app.get("/info")
def get_server_info():
    """获取综合服务器信息。"""
    info = {
        "server": {
            "name": "本地多模型AI网关",
            "version": "2.0.0",
            "description": "多个本地AI模型的统一API网关"
        },
        "features": {
            "mcp_enabled": mcp_server is not None,
            "model_routing": True,
            "health_monitoring": True,
            "statistics": True,
            "auth_enabled": is_auth_enabled()
        },
        "timestamp": time.time()
    }

    if mcp_server:
        info["mcp"] = {
            "server_name": mcp_server.name,
            "version": mcp_server.version,
            "tools_count": len(mcp_server._tools) if hasattr(mcp_server, '_tools') else 0
        }

    return info


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """以一致的格式处理HTTP异常。"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_exception",
                "detail": exc.detail,
                "status_code": exc.status_code
            },
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理一般异常。"""
    from fastapi.responses import JSONResponse
    logger.exception(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "detail": "内部服务器错误",
                "message": str(exc)
            },
            "timestamp": time.time()
        }
    )


if __name__ == "__main__":
    import uvicorn

    print("🚀 启动本地多模型AI网关")
    print("=" * 50)
    print(f"服务器: {app.title}")
    print(f"版本: {app.version}")
    print(f"MCP启用: {'✅' if mcp_server else '❌'}")
    print(f"认证: {'✅' if is_auth_enabled() else '❌'}")

    if is_auth_enabled():
        print("🔐 API密钥认证已启用")
        print("   请求头: X-API-Key")
        print("   环境变量: GATEWAY_API_KEY")
    else:
        print("🔓 API密钥认证已禁用")
        print("   设置GATEWAY_API_KEY环境变量以启用")

    if mcp_server:
        print(f"MCP服务器: {mcp_server.name} v{mcp_server.version}")
        tools = asyncio.run(mcp_server.list_tools())
        print(f"MCP工具: {len(tools)} 个已注册")

    print("\n📋 可用端点:")
    print("  POST /chat        - 与AI模型聊天")
    print("  GET  /models      - 列出可用模型")
    print("  GET  /health      - 健康检查")
    print("  GET  /stats       - 服务器统计")
    print("  GET  /info        - 服务器信息")
    print("  GET  /auth/status - 认证状态")
    print("  POST /auth/generate-key - 生成API密钥（仅开发用）")
    print("  GET  /auth/test   - 测试认证")

    if mcp_server:
        print("  POST /mcp         - MCP协议端点（需要认证）")
        print("  GET  /mcp/tools   - 列出MCP工具")
        print("  POST /mcp/tools/{name} - 调用MCP工具")

    print("\n🌐 在 http://0.0.0.0:8000 上启动服务器")
    print("按 Ctrl+C 停止")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
        access_log=True
    )
