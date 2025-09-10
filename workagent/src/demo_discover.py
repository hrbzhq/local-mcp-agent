import sys
import os
import json

# ensure src is on sys.path
# Ensure the package root is on sys.path so relative imports inside modules work
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, workspace_root)

from src.model_manager import ModelManager

mm = ModelManager()

query = "9月20日 北京 东京 机票 价格"
res = mm.discover_and_attempt(query)
print(json.dumps(res, ensure_ascii=False, indent=2))
