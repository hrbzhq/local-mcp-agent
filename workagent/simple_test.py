#!/usr/bin/env python3
import requests
import json
import time

def main():
    print('🔥 测试修复后的百度热搜查询功能')
    print('=' * 60)
    
    # 等待服务器稳定
    time.sleep(2)
    
    try:
        # 测试1：百度热搜查询
        print('📝 测试1: 查找百度热搜的前10条')
        resp = requests.post(
            'http://localhost:5000/api/tasks', 
            json={'task': '查找百度热搜的前10条', 'model': 'qwen3'},
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f'✅ 成功! 状态: {result.get("status")}')
            print(f'🤖 模型: {result.get("model")}')
            
            if 'capability' in result:
                print(f'🎯 检测到能力: {result["capability"]}')
            
            result_text = result.get('result', '无结果')
            print(f'📋 结果预览 ({len(result_text)} 字符):')
            print('-' * 50)
            print(result_text[:500])
            if len(result_text) > 500:
                print('...(省略更多内容)')
            print('-' * 50)
        else:
            print(f'❌ 失败: HTTP {resp.status_code}')
            print(f'错误: {resp.text}')
            
    except Exception as e:
        print(f'❌ 连接错误: {e}')
    
    # 测试2：热搜相关MCP查询
    print('\n' + '=' * 60)
    print('📝 测试2: @web微博热搜查询')
    
    try:
        resp = requests.post(
            'http://localhost:5000/api/tasks', 
            json={'task': '@web微博热搜', 'model': 'qwen3'},
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f'✅ 成功! 状态: {result.get("status")}')
            if 'capability' in result:
                print(f'🎯 检测到能力: {result["capability"]}')
            
            result_text = result.get('result', '无结果')
            print(f'📋 结果预览: {result_text[:300]}...')
        else:
            print(f'❌ 失败: HTTP {resp.status_code}')
            
    except Exception as e:
        print(f'❌ 连接错误: {e}')
    
    print('\n✅ 测试完成!')
    print('💡 请在浏览器中查看: http://localhost:5000')

if __name__ == '__main__':
    main()
