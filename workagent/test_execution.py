#!/usr/bin/env python3
import requests
import json
import time

def test_enhanced_execution():
    print('🚀 测试增强的自动执行功能')
    print('=' * 60)
    
    # 等待服务器稳定
    time.sleep(3)
    
    try:
        # 测试实时百度热搜查询
        print('📝 测试: 列出百度热搜的前10条')
        resp = requests.post(
            'http://localhost:5000/api/tasks', 
            json={'task': '列出百度热搜的前10条', 'model': 'qwen3'},
            timeout=45  # 增加超时时间，因为要执行网络请求
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f'✅ 成功! 状态: {result.get("status")}')
            print(f'🤖 模型: {result.get("model")}')
            
            if 'capability' in result:
                print(f'🎯 检测到能力: {result["capability"]}')
            
            result_text = result.get('result', '无结果')
            print(f'📋 结果 ({len(result_text)} 字符):')
            print('-' * 60)
            
            # 如果结果包含实时数据，高亮显示
            if '实时热搜结果' in result_text:
                print('🔥 LIVE DATA DETECTED! 🔥')
                
            print(result_text)
            print('-' * 60)
            
        else:
            print(f'❌ 失败: HTTP {resp.status_code}')
            print(f'错误: {resp.text}')
            
    except Exception as e:
        print(f'❌ 连接错误: {e}')
    
    print('\n✅ 测试完成!')
    
if __name__ == '__main__':
    test_enhanced_execution()
