import importlib
import sys
from pathlib import Path

# Ensure workspace root is on sys.path so 'src' can be imported by plugins
workspace_root = Path(__file__).resolve().parent
# add workagent dir so plugins using 'from src...' inside workagent resolve correctly
workagent_dir = str(workspace_root)
if workagent_dir not in sys.path:
    sys.path.insert(0, workagent_dir)

mods = ['workagent.plugins.data_processing_handler','workagent.plugins.mcp_advanced_analytics']
for m in mods:
    try:
        mod = importlib.import_module(m)
        members = [name for name in dir(mod) if not name.startswith('_')]
        print(f"{m} imported, members: {members}")
    except Exception as e:
        print(f"{m} import error: {e}")
