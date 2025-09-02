#!/usr/bin/env python3
"""
简单聊天示例 - Local MCP Agent 基础使用
演示如何与本地AI模型进行基本对话
"""

import requests
import json
import time
from typing import Optional

# 配置
BASE_URL = "http://localhost:8000"
DEFAULT_MODEL = "auto"  # 自动选择模型

class MCPChatClient:
    """简单的MCP聊天客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 验证服务器连接
        if not self._check_server():
            raise ConnectionError(f"无法连接到MCP服务器: {base_url}")
    
    def _check_server(self) -> bool:
        """检查服务器是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def chat(self, message: str, model: str = DEFAULT_MODEL) -> dict:
        """
        发送聊天消息
        
        Args:
            message: 要发送的消息
            model: 使用的模型，默认自动选择
            
        Returns:
            包含响应和元数据的字典
        """
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={
                    "input": message,
                    "model": model,
                    "temperature": 0.7
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            return {
                "error": f"请求失败: {str(e)}",
                "output": "抱歉，我现在无法回应。请检查网络连接和服务器状态。"
            }
    
    def get_available_models(self) -> list:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.RequestException:
            return []

def print_response(response: dict):
    """格式化打印响应"""
    print("\n" + "="*50)
    
    if "error" in response:
        print(f"❌ 错误: {response['error']}")
        return
    
    print(f"🤖 模型: {response.get('model', 'unknown')}")
    print(f"📝 回答:")
    print(response.get('output', '无响应'))
    
    # 显示元数据
    if 'meta' in response:
        meta = response['meta']
        print(f"\n📊 元信息:")
        print(f"   延迟: {meta.get('latency_ms', 0):.0f}ms")
        print(f"   输入tokens: {meta.get('input_tokens', 0)}")
        print(f"   输出tokens: {meta.get('output_tokens', 0)}")

def main():
    """主函数 - 交互式聊天演示"""
    print("🚀 Local MCP Agent - 简单聊天示例")
    print("输入 'quit' 或 'exit' 退出程序")
    print("输入 'models' 查看可用模型")
    print("输入 'help' 查看帮助")
    
    # 初始化客户端
    try:
        client = MCPChatClient()
        print(f"✅ 成功连接到服务器: {BASE_URL}")
    except ConnectionError as e:
        print(f"❌ {e}")
        print("请确保MCP服务器正在运行: python server/api_server.py")
        return
    
    # 获取可用模型
    models = client.get_available_models()
    if models:
        print(f"📋 可用模型: {', '.join(models)}")
    
    print("\n" + "="*50)
    
    # 交互式聊天循环
    while True:
        try:
            # 获取用户输入
            user_input = input("\n💬 您: ").strip()
            
            if not user_input:
                continue
                
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            elif user_input.lower() == 'models':
                models = client.get_available_models()
                print(f"📋 可用模型: {models}")
                continue
            elif user_input.lower() == 'help':
                print("""
📖 帮助信息:
- 直接输入消息与AI对话
- 'models' - 查看可用模型  
- 'quit/exit' - 退出程序
- 支持中英文对话
- 系统会自动选择最适合的模型
                """)
                continue
            
            # 发送聊天请求
            print("\n🤔 思考中...")
            start_time = time.time()
            
            response = client.chat(user_input)
            
            # 显示响应
            print_response(response)
            
            # 显示总耗时
            total_time = time.time() - start_time
            print(f"\n⏱️  总耗时: {total_time:.2f}秒")
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    # 示例对话
    demo_questions = [
        "你好，介绍一下你自己",
        "写一个Python的Hello World程序",
        "解释什么是递归算法",
        "推荐一本关于机器学习的书籍"
    ]
    
    print("🎯 快速演示模式")
    print("1. 交互式聊天")
    print("2. 预设问题演示")
    
    choice = input("请选择模式 (1/2): ").strip()
    
    if choice == "2":
        # 演示模式
        try:
            client = MCPChatClient()
            print("\n🎬 开始演示...")
            
            for i, question in enumerate(demo_questions, 1):
                print(f"\n📝 演示 {i}/{len(demo_questions)}: {question}")
                response = client.chat(question)
                print_response(response)
                
                if i < len(demo_questions):
                    input("\n按回车继续下一个演示...")
                    
        except Exception as e:
            print(f"❌ 演示失败: {e}")
    else:
        # 交互模式
        main()
