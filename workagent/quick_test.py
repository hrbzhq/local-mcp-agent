import requests
import json

print('🚀 测试机票价格查询')
try:
    resp = requests.post('http://localhost:5000/api/tasks', 
                        json={'task': '9月22日北京到东京的机票价格', 'model': 'qwen3'},
                        timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        print(f'✅ 成功! 状态: {result.get("status")}')
        if 'capability' in result:
            print(f'🎯 检测到能力: {result["capability"]}')
        print('结果预览:')
        result_text = result.get('result', '无结果')
        print(result_text[:300] + '...' if len(result_text) > 300 else result_text)
    else:
        print(f'❌ 失败: {resp.status_code}')
        print(resp.text)
except Exception as e:
    print(f'❌ 错误: {e}')
