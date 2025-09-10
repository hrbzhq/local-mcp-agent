import requests
import json

print('🚀 测试完整响应')
try:
    resp = requests.post('http://localhost:5000/api/tasks', 
                        json={'task': '查询12月1日上海到纽约的机票价格', 'model': 'qwen3'},
                        timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        print(f'✅ 成功! 状态: {result.get("status")}')
        print(f'模型: {result.get("model")}')
        if 'capability' in result:
            print(f'🎯 检测到能力: {result["capability"]}')
        
        print('\n完整结果:')
        print('=' * 60)
        print(result.get('result', '无结果'))
        print('=' * 60)
    else:
        print(f'❌ 失败: {resp.status_code}')
        print(resp.text)
except Exception as e:
    print(f'❌ 错误: {e}')
