import requests
import time

print('等待服务器稳定...')
time.sleep(10)

print('🚀 测试最终修复')
try:
    resp = requests.post(
        'http://localhost:5000/api/tasks', 
        json={'task': '百度热搜前5条', 'model': 'qwen3'},
        timeout=60
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f'✅ 状态: {result.get("status")}')
        print(f'🤖 模型: {result.get("model")}')
        
        result_text = result.get('result', '')
        print(f'📋 结果类型: {"实时数据!" if "实时热搜结果" in result_text else "学习结果"}')
        print(f'📋 结果预览:')
        print('-' * 40)
        print(result_text[:400])
        if len(result_text) > 400:
            print('...(更多内容)')
        print('-' * 40)
        
    else:
        print(f'❌ HTTP错误: {resp.status_code}')
        
except Exception as e:
    print(f'❌ 连接错误: {e}')

print('测试完成')
