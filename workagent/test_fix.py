#!/usr/bin/env python3
"""
测试修复后的自动学习功能
"""

import requests
import json
import time

def test_single_query():
    """测试单个查询"""
    
    print("🚀 测试修复后的自动学习功能")
    print("="*50)
    
    # 测试机票查询
    test_data = {
        "task": "9月22日北京到东京的机票价格",
        "model": "qwen3"
    }
    
    try:
        print(f"📝 发送查询: {test_data['task']}")
        
        response = requests.post(
            "http://localhost:5000/api/tasks",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 查询成功!")
            print(f"状态: {result.get('status')}")
            print(f"使用模型: {result.get('model')}")
            
            if 'capability' in result:
                print(f"🎯 检测到的能力: {result['capability']}")
            
            print("\n📋 响应结果:")
            print("-" * 40)
            result_text = result.get('result', '无结果')
            # 如果结果太长，截取前500字符
            if len(result_text) > 500:
                print(result_text[:500] + "...")
            else:
                print(result_text)
            print("-" * 40)
            
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_direct_mcp():
    """测试直接MCP查询"""
    
    print("\n🔍 测试直接MCP查询")
    print("="*30)
    
    test_data = {
        "task": "@web 机票价格 北京 东京 9月22日",
        "model": "qwen3"
    }
    
    try:
        print(f"📝 发送MCP查询: {test_data['task']}")
        
        response = requests.post(
            "http://localhost:5000/api/tasks",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP查询成功!")
            print(f"状态: {result.get('status')}")
            
            result_text = result.get('result', '无结果')
            if len(result_text) > 300:
                print(f"结果: {result_text[:300]}...")
            else:
                print(f"结果: {result_text}")
        else:
            print(f"❌ MCP查询失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ MCP测试失败: {e}")

if __name__ == "__main__":
    print("开始测试修复后的功能...")
    
    # 等待服务器启动
    time.sleep(3)
    
    # 测试自动学习功能
    test_single_query()
    
    # 测试MCP功能
    test_direct_mcp()
    
    print("\n✅ 测试完成!")
    print("请检查Web界面: http://localhost:5000")
