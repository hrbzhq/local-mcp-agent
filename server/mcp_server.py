"""本地多模型网关的 MCP 服务器。

实现了一个 Model Context Protocol（MCP）服务器，使 AI 模型能够将本地多模型
网关作为工具进行交互，从而支持智能体（agent）之间的协作。
"""
import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Sequence, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import Depends

# Import our existing modules
from router import select_model
from model_manager import call_model, list_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolError(Exception):
    """工具执行错误的自定义异常。"""
    pass


class ToolStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ToolResult:
    """工具执行的结构化结果。"""
    status: ToolStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典以便 JSON 序列化。"""
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass
class ToolDefinition:
    """MCP 工具的定义。"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]
    timeout: float = 30.0  # Default 30 second timeout


class MCPServer:
    """正式的 MCP 服务器，用于管理本地多模型网关的工具。

    该服务器为 AI 智能体提供一个清晰、可扩展的接口，通过标准化的工具调用
    与多个本地模型进行交互。
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._tools: Dict[str, ToolDefinition] = {}
        self._stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time": 0.0
        }
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具集合。"""
        self.register_tool(ToolDefinition(
            name="chat_with_model",
            description="与指定 AI 模型对话，或根据内容自动选择模型",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "发送给模型的输入文本"
                    },
                    "model": {
                        "type": "string",
                        "description": "可选：使用的特定模型（未提供则自动选择）"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "可选：用于上下文的用户标识",
                        "default": "anonymous"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "可选：模型温度 (0.0 到 1.0)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    }
                },
                "required": ["input"]
            },
            handler=self._handle_chat_with_model
        ))

        self.register_tool(ToolDefinition(
            name="list_available_models",
            description="列出本地网关中所有可用模型及其能力",
            input_schema={
                "type": "object",
                "properties": {
                    "include_details": {
                        "type": "boolean",
                        "description": "是否包含模型的详细信息",
                        "default": False
                    }
                },
                "required": []
            },
            handler=self._handle_list_models
        ))

        self.register_tool(ToolDefinition(
            name="collaborative_chat",
            description="启动多个模型之间的协作对话",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "协作的初始输入"
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "参与协作的模型列表",
                        "minItems": 1
                    },
                    "max_rounds": {
                        "type": "integer",
                        "description": "最大协作轮数",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3
                    },
                    "strategy": {
                        "type": "string",
                        "description": "协作策略",
                        "enum": ["sequential", "parallel", "consensus"],
                        "default": "sequential"
                    }
                },
                "required": ["input", "models"]
            },
            handler=self._handle_collaborative_chat,
            timeout=120.0  # Longer timeout for collaboration
        ))

    def register_tool(self, tool_def: ToolDefinition):
        """Register a new tool with the server."""
        if tool_def.name in self._tools:
            logger.warning(f"工具 '{tool_def.name}' 已存在，正在覆盖")
        self._tools[tool_def.name] = tool_def
        logger.info(f"已注册工具: {tool_def.name}")

    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the server."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
        else:
            logger.warning(f"Tool '{tool_name}' not found for unregistration")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Return metadata for all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self._tools.values()
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        start_time = time.time()

        try:
            # 验证工具是否存在
            if name not in self._tools:
                raise ToolError(f"未知工具: {name}")

            tool_def = self._tools[name]

            # 根据 schema 验证参数
            self._validate_arguments(arguments, tool_def.input_schema)

            # Execute tool with timeout
            result = await asyncio.wait_for(
                tool_def.handler(arguments),
                timeout=tool_def.timeout
            )

            execution_time = time.time() - start_time

            # 更新统计信息
            self._update_stats(success=True, execution_time=execution_time)

            tool_result = ToolResult(
                status=ToolStatus.SUCCESS,
                data=result,
                execution_time=execution_time,
                tool_name=name,
                timestamp=start_time
            )

            return tool_result.to_dict()

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self._update_stats(success=False, execution_time=execution_time)
            tool_result = ToolResult(
                status=ToolStatus.TIMEOUT,
                error=f"Tool '{name}' timed out after {tool_def.timeout}s",
                execution_time=execution_time,
                tool_name=name,
                timestamp=start_time
            )
            return tool_result.to_dict()

        except Exception as e:
            execution_time = time.time() - start_time
            self._update_stats(success=False, execution_time=execution_time)
            logger.exception(f"工具 '{name}' 执行失败: {e}")
            tool_result = ToolResult(
                status=ToolStatus.ERROR,
                error=str(e),
                execution_time=execution_time,
                tool_name=name,
                timestamp=start_time
            )
            return tool_result.to_dict()

    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]):
        """Basic argument validation against schema."""
        required = schema.get("required", [])
        for field in required:
            if field not in arguments:
                raise ToolError(f"缺少必需参数: {field}")

        properties = schema.get("properties", {})
        for arg_name, arg_value in arguments.items():
            if arg_name in properties:
                prop_schema = properties[arg_name]
                self._validate_argument_value(arg_name, arg_value, prop_schema)

    def _validate_argument_value(self, name: str, value: Any, schema: Dict[str, Any]):
        """Validate a single argument value."""
        arg_type = schema.get("type")
        if arg_type == "string" and not isinstance(value, str):
            raise ToolError(f"参数 '{name}' 必须是字符串")
        elif arg_type == "number" and not isinstance(value, (int, float)):
            raise ToolError(f"参数 '{name}' 必须是数字")
        elif arg_type == "integer" and not isinstance(value, int):
            raise ToolError(f"参数 '{name}' 必须是整数")
        elif arg_type == "boolean" and not isinstance(value, bool):
            raise ToolError(f"参数 '{name}' 必须是布尔值")
        elif arg_type == "array" and not isinstance(value, list):
            raise ToolError(f"参数 '{name}' 必须是数组")

        # Check constraints
        if "minimum" in schema and isinstance(value, (int, float)) and value < schema["minimum"]:
            raise ToolError(f"参数 '{name}' 必须 >= {schema['minimum']}")
        if "maximum" in schema and isinstance(value, (int, float)) and value > schema["maximum"]:
            raise ToolError(f"参数 '{name}' 必须 <= {schema['maximum']}")
        if "minItems" in schema and isinstance(value, list) and len(value) < schema["minItems"]:
            raise ToolError(f"参数 '{name}' 至少需要 {schema['minItems']} 个元素")
        if "enum" in schema and value not in schema["enum"]:
            raise ToolError(f"参数 '{name}' 必须是以下之一: {schema['enum']}")

    def _update_stats(self, success: bool, execution_time: float):
        """Update server statistics."""
        self._stats["total_calls"] += 1
        if success:
            self._stats["successful_calls"] += 1
        else:
            self._stats["failed_calls"] += 1

        # Update rolling average
        total_time = self._stats["average_execution_time"] * (self._stats["total_calls"] - 1)
        self._stats["average_execution_time"] = (total_time + execution_time) / self._stats["total_calls"]

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return self._stats.copy()

    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status."""
        return {
            "status": "healthy",
            "server_name": self.name,
            "version": self.version,
            "tools_registered": len(self._tools),
            "uptime": time.time(),
            **self._stats
        }

    # Tool handlers
    async def _handle_chat_with_model(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理单模型聊天请求，包含增强功能。"""
        input_text = arguments.get("input", "").strip()
        model = arguments.get("model", "").strip()
        user_id = arguments.get("user_id", "anonymous")
        temperature = arguments.get("temperature", 0.7)

        if not input_text:
            raise ToolError("输入文本不能为空")

        # Auto-select model if not specified
        if not model:
            model = select_model(input_text)
            logger.info(f"自动选择模型 '{model}'，输入预览: {input_text[:50]}...")

        # Validate model exists
        available_models = list_models()
        if model not in available_models:
            raise ToolError(f"模型 '{model}' 不可用。可用模型: {available_models}")

        # Call the model
        result = call_model(model, input_text)

        response = {
            "model": model,
            "input": input_text,
            "output": result.get("output", ""),
            "user_id": user_id,
            "temperature": temperature,
            "timestamp": time.time(),
            "metadata": {
                "model_selected": "auto" if not arguments.get("model") else "manual",
                "input_length": len(input_text),
                "output_length": len(result.get("output", ""))
            }
        }

        return response

    async def _handle_list_models(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理模型列表请求，可选择返回详细信息。"""
        include_details = arguments.get("include_details", False)

        models = list_models()
        response = {
            "models": models,
            "count": len(models),
            "timestamp": time.time()
        }

        if include_details:
            # Add detailed information about each model
            detailed_models = []
            for model in models:
                model_info = {
                    "name": model,
                    "description": f"本地模型: {model}",
                    "capabilities": self._get_model_capabilities(model),
                    "status": "available"
                }
                detailed_models.append(model_info)
            response["detailed_models"] = detailed_models

        return response

    async def _handle_collaborative_chat(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理多模型协作对话，支持多种协作策略。"""
        input_text = arguments.get("input", "").strip()
        models = arguments.get("models", [])
        max_rounds = arguments.get("max_rounds", 3)
        strategy = arguments.get("strategy", "sequential")

        if not input_text:
            raise ToolError("输入文本不能为空")
        if not models:
            raise ToolError("模型列表不能为空")

        # Validate all models exist
        available_models = list_models()
        invalid_models = [m for m in models if m not in available_models]
        if invalid_models:
            raise ToolError(f"无效模型: {invalid_models}。可用模型: {available_models}")

        collaboration_history = []
        current_input = input_text

        if strategy == "sequential":
            # Sequential collaboration: each model builds on previous output
            for round_num in range(max_rounds):
                round_results = []

                for model in models:
                    result = call_model(model, current_input)
                    response = {
                        "round": round_num + 1,
                        "model": model,
                        "input": current_input,
                        "output": result.get("output", ""),
                        "timestamp": time.time()
                    }
                    round_results.append(response)

                collaboration_history.append({
                    "round": round_num + 1,
                    "strategy": "sequential",
                    "responses": round_results
                })

                # Use the last model's output as input for next round
                if round_results:
                    current_input = round_results[-1]["output"]

        elif strategy == "parallel":
            # Parallel collaboration: all models respond to same input
            for round_num in range(max_rounds):
                round_results = []

                for model in models:
                    result = call_model(model, current_input)
                    response = {
                        "round": round_num + 1,
                        "model": model,
                        "input": current_input,
                        "output": result.get("output", ""),
                        "timestamp": time.time()
                    }
                    round_results.append(response)

                collaboration_history.append({
                    "round": round_num + 1,
                    "strategy": "parallel",
                    "responses": round_results
                })

                # Combine all outputs for next round
                if round_results:
                    combined_output = "\n\n".join([r["output"] for r in round_results])
                    current_input = f"Previous responses:\n{combined_output}\n\nPlease continue the discussion."

        elif strategy == "consensus":
            # Consensus-based collaboration
            for round_num in range(max_rounds):
                round_results = []

                for model in models:
                    result = call_model(model, current_input)
                    response = {
                        "round": round_num + 1,
                        "model": model,
                        "input": current_input,
                        "output": result.get("output", ""),
                        "timestamp": time.time()
                    }
                    round_results.append(response)

                collaboration_history.append({
                    "round": round_num + 1,
                    "strategy": "consensus",
                    "responses": round_results
                })

                # Create consensus input for next round
                if round_results:
                    outputs = [r["output"] for r in round_results]
                    consensus_input = f"""Based on these {len(outputs)} responses:

{chr(10).join(f'{i+1}. {output}' for i, output in enumerate(outputs))}

Please provide a consensus or synthesis of these viewpoints."""
                    current_input = consensus_input

        final_response = {
            "collaboration_summary": {
                "initial_input": input_text,
                "models_involved": models,
                "total_rounds": len(collaboration_history),
                "strategy": strategy,
                "final_output": current_input,
                "timestamp": time.time()
            },
            "detailed_history": collaboration_history,
            "statistics": {
                "total_responses": sum(len(round_data["responses"]) for round_data in collaboration_history),
                "models_participated": len(set(models)),
                "average_responses_per_round": len(models)
            }
        }

        return final_response

    def _get_model_capabilities(self, model_name: str) -> List[str]:
        """根据模型名推断模型的能力。"""
        capabilities = []

        # Infer capabilities from model name
        name_lower = model_name.lower()
        if "coder" in name_lower or "code" in name_lower:
            capabilities.extend(["coding", "programming", "debugging", "code_generation"])
        if "vl" in name_lower or "vision" in name_lower:
            capabilities.extend(["vision", "image_understanding", "multimodal"])
        if "deepseek" in name_lower or "r1" in name_lower:
            capabilities.extend(["reasoning", "analysis", "long_context"])
        if "gemma" in name_lower:
            capabilities.extend(["fast_inference", "lightweight", "general_purpose"])

        # Default capabilities
        if not capabilities:
            capabilities = ["text_generation", "conversation", "general_purpose"]

        return capabilities


# Global MCP server instance
mcp_server = MCPServer("local-multi-model-gateway")


async def handle_mcp_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests."""
    method = request_data.get("method", "")
    params = request_data.get("params", {})

    if method == "tools/list":
        tools = await mcp_server.list_tools()
        return {"tools": tools}

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        result = await mcp_server.call_tool(tool_name, tool_args)
        return {"result": result}

    else:
        return {"error": f"Unknown method: {method}"}


# Integration with existing FastAPI server
def integrate_with_fastapi(app):
    """Integrate MCP functionality with the existing FastAPI app."""
    # Backwards-compatible integration: accept optional auth dependencies
    # Usage: integrate_with_fastapi(app, require_auth=..., optional_auth=...)
    def _integrate(require_auth: Optional[Callable] = None, optional_auth: Optional[Callable] = None):
        # /mcp endpoint - requires auth if provided
        if require_auth:
            @app.post("/mcp")
            async def mcp_endpoint(request: Dict[str, Any], user: str = Depends(require_auth)):
                """MCP protocol endpoint (protected)."""
                return await handle_mcp_request(request)
        else:
            @app.post("/mcp")
            async def mcp_endpoint(request: Dict[str, Any]):
                """MCP protocol endpoint."""
                return await handle_mcp_request(request)

        # /mcp/tools - list tools (allow optional auth)
        if optional_auth:
            @app.get("/mcp/tools")
            async def list_mcp_tools(user: Optional[str] = Depends(optional_auth)):
                """List available MCP tools (optional auth)."""
                tools = await mcp_server.list_tools()
                return {"tools": tools}
        else:
            @app.get("/mcp/tools")
            async def list_mcp_tools():
                """List available MCP tools."""
                tools = await mcp_server.list_tools()
                return {"tools": tools}

        # /mcp/tools/{tool_name} - call a tool (requires auth if provided)
        if require_auth:
            @app.post("/mcp/tools/{tool_name}")
            async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any] = None, user: str = Depends(require_auth)):
                """Call a specific MCP tool (protected)."""
                if arguments is None:
                    arguments = {}
                result = await mcp_server.call_tool(tool_name, arguments)
                return result
        else:
            @app.post("/mcp/tools/{tool_name}")
            async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any] = None):
                """Call a specific MCP tool."""
                if arguments is None:
                    arguments = {}
                result = await mcp_server.call_tool(tool_name, arguments)
                return result

        # Health: only register if app doesn't already provide /health
        existing_paths = {r.path for r in getattr(app, 'routes', [])}
        if "/health" not in existing_paths:
            @app.get("/health")
            async def health_check():
                """Health check endpoint."""
                return mcp_server.get_health_status()

    # Allow callers to pass auth dependencies via attributes on the app if present
    # This keeps the integration call simple: integrate_with_fastapi(app)
    require = getattr(app, "require_auth", None)
    optional = getattr(app, "optional_auth", None)
    _integrate(require_auth=require, optional_auth=optional)


if __name__ == "__main__":
    print("MCP Server for Local Multi-Model Gateway")
    print(f"Server Name: {mcp_server.name}")
    print(f"Version: {mcp_server.version}")
    print("\nRegistered tools:")
    tools = asyncio.run(mcp_server.list_tools())
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")

    print("\nServer is ready for integration with FastAPI or other frameworks.")
