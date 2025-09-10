#!/usr/bin/env python3
"""
测试自动能力学习功能的演示脚本
"""

import sys
import os

# 确保项目路径在sys.path中
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, workspace_root)

from src.model_manager import ModelManager


def test_auto_learning():
    """测试自动学习功能"""
    print("🚀 测试自动能力学习功能\n")
    
    mm = ModelManager()
    
    # 测试查询列表
    test_queries = [
        "9月22日北京到东京的机票价格",
        "明天上海飞纽约多少钱",
        "查询股票价格API",
        "天气查询代码示例"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{'='*60}")
        print(f"测试 {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # 使用发现并尝试功能
            result = mm.discover_and_attempt(query)
            
            print(f"状态: {result.get('status', 'unknown')}")
            if 'result' in result:
                print(f"结果: {result['result']}")
            elif 'raw' in result:
                print(f"原始响应: {result['raw'][:500]}...")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"安全分析: 网络调用={analysis.get('contains_network_calls')}, "
                      f"Shell调用={analysis.get('contains_shell')}, "
                      f"安全执行={analysis.get('safe_to_exec')}")
            
            print()
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print()


if __name__ == "__main__":
    test_auto_learning()
