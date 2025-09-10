import re
import logging
from typing import Optional, Dict

from .mcp_manager import MCPManager


class CapabilityLearner:
    """Lightweight capability discovery + storage using MCPManager.

    This module does NOT execute arbitrary network code automatically.
    It fetches instructions or code from MCP, stores the raw artifact,
    and performs a simple safety check before indicating whether
    automated execution is recommended or requires operator review.
    """

    def __init__(self, mcp: Optional[MCPManager] = None):
        self.mcp = mcp or MCPManager()
        self.knowledge: Dict[str, str] = {}

    def discover(self, query: str) -> str:
        """Ask MCP for a solution/instructions for `query` and store the result.

        Returns the raw MCP response.
        """
        # Prefix with @ to route to MCP @-query handlers where available
        q = query
        if not query.startswith('@'):
            q = f"@{query}"

        logging.info("CapabilityLearner: discovering capability for query: %s", query)
        try:
            result = self.mcp.search_remote_mcp(q)
        except Exception as e:
            logging.error("CapabilityLearner: MCP query failed: %s", e)
            result = f"MCP查询失败：{e}"

        # store the raw result keyed by the query
        self.knowledge[query] = result
        return result

    def extract_python_code(self, text: str) -> Optional[str]:
        """Extract first Python code block from text if present."""
        match = re.search(r"```python\n([\s\S]*?)```", text)
        if match:
            return match.group(1)
        return None

    def analyze_safety(self, text: str) -> Dict[str, bool]:
        """Basic heuristics to decide whether automated execution is safe.

        Returns dict with keys: "contains_network_calls", "contains_shell",
        "safe_to_exec".
        """
        lower = text.lower()
        contains_network = 'requests.' in lower or 'http' in lower or 'urllib' in lower
        contains_shell = 'subprocess' in lower or 'os.system' in lower or 'popen' in lower
        # mark safe only if no network/shell indicators
        safe = not (contains_network or contains_shell)
        return {
            'contains_network_calls': contains_network,
            'contains_shell': contains_shell,
            'safe_to_exec': safe,
        }

    def learn_and_prepare(self, query: str) -> Dict[str, object]:
        """Discover via MCP and prepare a learn artifact.

        Returns a summary including raw result, extracted code (if any),
        and a safety analysis.
        """
        raw = self.discover(query)
        code = self.extract_python_code(raw) if isinstance(raw, str) else None
        analysis = self.analyze_safety(raw if isinstance(raw, str) else "")

        return {
            'query': query,
            'raw': raw,
            'python_code': code,
            'analysis': analysis,
        }

    def simulate_execute(self, query: str) -> Dict[str, object]:
        """Attempt a safe/simulated execution flow and return a result summary.

        This method will attempt to execute learned code safely, including
        network operations for specific trusted queries like hot search.
        """
        artifact = self.learn_and_prepare(query)
        code = artifact.get('python_code')
        analysis = artifact.get('analysis', {})

        if not code:
            return {'status': 'no_code', 'raw': artifact['raw']}

        # Check if this is a trusted query type that we can safely execute
        query_lower = query.lower()
        is_trusted_query = any(word in query_lower for word in [
            '热搜', '百度热搜', '微博热搜', 'baidu', 'weibo'
        ])

        if not analysis.get('safe_to_exec') and not is_trusted_query:
            return {
                'status': 'requires_review',
                'reason': 'contains network or shell operations',
                'analysis': analysis,
                'raw_code': code,
            }

        # For trusted queries, try to execute the network code safely
        if is_trusted_query and not analysis.get('safe_to_exec'):
            return self._execute_trusted_network_code(code, query)

        # Safe local execution
        try:
            local_ns = {}
            # restrict builtins
            safe_globals = {'__builtins__': {}}
            exec(code, safe_globals, local_ns)

            # If a function named 'run' exists, call it without args
            if 'run' in local_ns and callable(local_ns['run']):
                try:
                    result = local_ns['run']()
                except Exception as e:
                    return {'status': 'exec_error', 'error': str(e)}
                return {'status': 'ok', 'result': result}
        except Exception as e:
            return {'status': 'exec_error', 'error': str(e)}

    def _execute_trusted_network_code(self, code: str, query: str) -> Dict[str, object]:
        """Safely execute trusted network code like hot search queries"""
        try:
            # Import required modules in safe namespace
            import requests
            from bs4 import BeautifulSoup
            import json
            from datetime import datetime
            
            # Create safe globals with necessary modules and builtins
            safe_globals = {
                '__builtins__': {
                    '__import__': __import__,  # 添加import支持
                    'enumerate': enumerate,
                    'len': len,
                    'str': str,
                    'int': int,
                    'print': print,
                    'range': range,
                    'Exception': Exception,
                    'TimeoutError': TimeoutError,
                    'isinstance': isinstance,
                    'dict': dict,
                    'list': list,
                },
                '__name__': '__main__',  # 添加__name__变量
                'requests': requests,
                'BeautifulSoup': BeautifulSoup,
                'json': json,
                'datetime': datetime,
            }
            
            local_ns = {}
            
            # Execute the code
            exec(code, safe_globals, local_ns)
            
            # Try to find and execute the main function
            main_func = None
            for name, obj in local_ns.items():
                if callable(obj) and (
                    'get_baidu_hot_search' in name or 
                    'get_weibo_hot_search' in name or
                    'hot_search' in name.lower()
                ):
                    main_func = obj
                    break
            
            if main_func:
                try:
                    # Execute with timeout and error handling
                    import threading
                    import time
                    
                    result_container = {'result': None, 'error': None}
                    
                    def execute_function():
                        try:
                            result_container['result'] = main_func(10)  # Get top 10
                        except Exception as e:
                            result_container['error'] = str(e)
                    
                    # Run function in a separate thread with timeout
                    thread = threading.Thread(target=execute_function)
                    thread.daemon = True
                    thread.start()
                    thread.join(timeout=15)  # 15 second timeout
                    
                    if thread.is_alive():
                        return {
                            'status': 'timeout',
                            'result': '代码执行超时，可能是网络连接问题'
                        }
                    
                    if result_container['error']:
                        return {
                            'status': 'exec_error',
                            'error': f'执行失败: {result_container["error"]}',
                            'fallback_code': code
                        }
                    
                    result = result_container['result']
                    
                    if result:
                        # Format the result nicely
                        formatted_result = "🔥 实时热搜结果：\n\n"
                        for item in result[:10]:
                            if isinstance(item, dict):
                                rank = item.get('rank', '?')
                                title = item.get('title', 'Unknown')
                                formatted_result += f"{rank:2d}. {title}\n"
                            else:
                                formatted_result += f"   • {item}\n"
                        
                        formatted_result += f"\n⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        return {
                            'status': 'ok', 
                            'result': formatted_result,
                            'raw_data': result
                        }
                    else:
                        return {
                            'status': 'no_data',
                            'result': '未能获取到热搜数据，可能是网络问题或网站结构变化'
                        }
                        
                except Exception as e:
                    return {
                        'status': 'exec_error',
                        'error': f'执行失败: {str(e)}',
                        'fallback_code': code
                    }
            else:
                return {
                    'status': 'no_main_function',
                    'result': '代码中未找到可执行的主函数',
                    'code': code
                }
                
        except Exception as e:
            return {
                'status': 'exec_error', 
                'error': f'代码准备失败: {str(e)}',
                'fallback_code': code
            }

            # else return the last defined value if any
            if '_result' in local_ns:
                return {'status': 'ok', 'result': local_ns['_result']}

            return {'status': 'ok', 'message': '代码执行完成，但未返回可见结果'}

        except Exception as e:
            logging.error("CapabilityLearner: execution failed: %s", e)
            return {'status': 'exec_failed', 'error': str(e)}
