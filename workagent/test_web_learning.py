#!/usr/bin/env python3
"""
演示完整的自动能力学习工作流程
"""

import requests
import json
import time

def test_web_interface():
    """测试Web界面的自动学习功能"""
    
    base_url = "http://localhost:5000"
    
    # 测试查询列表
    test_queries = [
        {
            "task": "9月22日北京到东京的机票价格",
            "model": "qwen3",
            "expected_capability": "flight_price_query"
        },
        {
            "task": "查询明天上海的天气",
            "model": "qwen3", 
            "expected_capability": "weather_query"
        },
        {
            "task": "今天的股票市场新闻",
            "model": "qwen3",
            "expected_capability": "news_query"
        }
    ]
    
    print("🚀 测试Web界面自动能力学习功能\n")
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"{'='*70}")
        print(f"测试 {i}: {test_case['task']}")
        print(f"预期能力: {test_case['expected_capability']}")
        print(f"{'='*70}")
        
        try:
            # 发送POST请求到/api/tasks
            response = requests.post(
                f"{base_url}/api/tasks",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ 请求成功")
                print(f"状态: {result.get('status')}")
                print(f"使用模型: {result.get('model')}")
                
                if 'capability' in result:
                    print(f"🎯 检测到的能力: {result['capability']}")
                
                print(f"响应结果:")
                print("-" * 50)
                print(result.get('result', '无结果')[:500] + "...")
                print("-" * 50)
                
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()
        time.sleep(1)  # 避免请求过快

def test_direct_mcp_query():
    """直接测试MCP查询功能"""
    
    print("\n🔍 测试直接MCP查询功能")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    mcp_queries = [
        "@web 实时查询机票价格 API 代码示例 9月22日北京到东京",
        "@help",
        "@web 机票价格 北京 东京"
    ]
    
    for query in mcp_queries:
        print(f"\n查询: {query}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/api/tasks",
                json={"task": query, "model": "qwen3"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"状态: {result.get('status')}")
                print(f"结果: {result.get('result', '无结果')[:300]}...")
            else:
                print(f"失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    print("开始测试...")
    
    # 等待服务器启动
    time.sleep(2)
    
    # 测试自动学习功能
    test_web_interface()
    
    # 测试MCP查询功能
    test_direct_mcp_query()
    
    print("\n✅ 测试完成！")
    print("请查看Web界面 http://localhost:5000 进行交互式测试")
