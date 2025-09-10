import sys
from pathlib import Path
p = Path(__file__).resolve().parent
# ensure workagent package dir is importable
workagent_dir = str(p / 'workagent')
if workagent_dir not in sys.path:
    sys.path.insert(0, workagent_dir)

import ast, importlib, traceback
fpath = p / 'workagent' / 'plugins' / 'mcp_advanced_analytics.py'
print('Checking file:', fpath)
src = fpath.read_text(encoding='utf-8')
try:
    ast.parse(src)
    print('AST parse: OK')
except SyntaxError as e:
    print('AST parse: SyntaxError')
    traceback.print_exception(e, e, e.__traceback__)

print('\nAttempting import of workagent.plugins.mcp_advanced_analytics')
try:
    mod = importlib.import_module('workagent.plugins.mcp_advanced_analytics')
    print('Import succeeded. Members:', [n for n in dir(mod) if not n.startswith('_')])
except Exception as e:
    print('Import failed:')
    traceback.print_exception(e, e, e.__traceback__)
