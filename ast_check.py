import ast
p='workagent/plugins/mcp_advanced_analytics.py'
src=open(p,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('AST OK')
except SyntaxError as e:
    print('SyntaxError:', e)
except Exception as e:
    print('Error:', e)
