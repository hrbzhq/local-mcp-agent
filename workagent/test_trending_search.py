import requests
import json

print('🔥 测试百度热搜查询')
try:
    resp = requests.post('http://localhost:5000/api/tasks', 
                        json={'task': '查找百度热搜的前10条', 'model': 'qwen3'},
                        timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        print(f'✅ 成功! 状态: {result.get("status")}')
        print(f'模型: {result.get("model")}')
        if 'capability' in result:
            print(f'🎯 检测到能力: {result["capability"]}')
        
        print('\n完整结果:')
        print('=' * 80)
        result_text = result.get('result', '无结果')
        print(result_text[:1000] + '...' if len(result_text) > 1000 else result_text)
        print('=' * 80)
    else:
        print(f'❌ 失败: {resp.status_code}')
        print(resp.text)
except Exception as e:
    print(f'❌ 错误: {e}')

print('\n' + '='*50)
print('🔍 测试微博热搜查询')
try:
    resp = requests.post('http://localhost:5000/api/tasks', 
                        json={'task': '@web微博热搜', 'model': 'qwen3'},
                        timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        print(f'✅ 成功! 状态: {result.get("status")}')
        if 'capability' in result:
            print(f'🎯 检测到能力: {result["capability"]}')
        
        result_text = result.get('result', '无结果')
        print(f'结果预览: {result_text[:300]}...')
    else:
        print(f'❌ 失败: {resp.status_code}')
        print(resp.text)
except Exception as e:
    print(f'❌ 错误: {e}')
