import requests
import json

print('🚀 直接测试百度热搜功能')

try:
    response = requests.post(
        'http://127.0.0.1:5000/api/tasks',
        json={'task': '百度热搜前5条', 'model': 'qwen3'},
        timeout=45
    )
    
    print(f'HTTP状态码: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'任务状态: {data.get("status", "未知")}')
        print(f'使用模型: {data.get("model", "未知")}')
        
        result_text = data.get('result', '无结果')
        
        if '实时热搜结果' in result_text:
            print('🔥 SUCCESS! 检测到实时执行结果!')
        elif 'MCP学习' in result_text:
            print('📚 学习模式 - 提供了代码示例')
        else:
            print('📋 普通响应')
            
        print('\n结果预览:')
        print('=' * 50)
        print(result_text[:500])
        if len(result_text) > 500:
            print('\n...(更多内容)')
        print('=' * 50)
        
    else:
        print(f'请求失败: {response.status_code}')
        print(f'错误内容: {response.text}')
        
except requests.exceptions.RequestException as e:
    print(f'网络请求错误: {e}')
except Exception as e:
    print(f'其他错误: {e}')

print('\n测试完成!')
