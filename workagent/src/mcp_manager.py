import sqlite3
import os
from datetime import datetime


class MCPManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), '..', 'mcp', 'mcp_cache.db'
            )
        self.db_path = os.path.abspath(db_path)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mcp_modules (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    content TEXT,
                    source TEXT,
                    created_at TIMESTAMP
                )
            ''')

    def get_mcp(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT content FROM mcp_modules WHERE name = ?', (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def save_mcp(self, name, content, source='local'):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO mcp_modules (name, content, source, created_at)
                VALUES (?, ?, ?, ?)
            ''', (name, content, source, datetime.now()))

    def search_remote_mcp(self, query):
        """实现远程MCP查询逻辑"""
        try:
            # 处理@查询 - 明确指定为MCP查询
            if query.startswith('@'):
                actual_query = query[1:].strip()  # 移除@符号
                print(f"🔍 处理@查询: {actual_query}")

                # 检查本地缓存
                cached_result = self.get_mcp(f"@{actual_query}")
                if cached_result:
                    return cached_result

                # 处理不同类型的@查询
                return self._handle_at_query(actual_query)

            # 这里可以实现多种MCP查询方式
            # 1. GitHub搜索
            # 2. 专门的MCP仓库
            # 3. 本地缓存的MCP模块

            # 首先检查本地缓存
            cached_result = self.get_mcp(query)
            if cached_result:
                return cached_result

            # 如果没有缓存，尝试从GitHub或其他来源获取
            import requests

            # 示例：从GitHub搜索相关代码或文档
            if "web_content:" in query:
                url = query.replace("web_content:", "")
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        content = response.text[:1000]  # 限制内容长度
                        self.save_mcp(query, content, f"web:{url}")
                        return content
                except Exception as e:
                    # 远程获取失败，忽略但记录到标准输出以便调试
                    print(f"Warning: failed to fetch web content {url}: {e}")

            elif "code_examples:" in query:
                # 搜索编程相关的示例
                search_term = query.replace("code_examples:", "")
                # 这里可以调用GitHub API或其他代码搜索服务
                mock_examples = f"""
                以下是关于"{search_term}"的代码示例：

                # Python示例
                def example_function():
                    '''这是一个示例函数'''
                    return "Hello, World!"

                # 使用示例
                result = example_function()
                print(result)
                """
                self.save_mcp(query, mock_examples, "code_examples")
                return mock_examples

            elif "train_schedule:" in query:
                # 高铁时刻表查询
                train_number = query.replace("train_schedule:", "").strip()
                try:
                    # 这里可以调用真实的铁路API或模拟数据
                    # 为了演示，我们返回模拟的高铁时刻表数据
                    mock_schedule = f"""
                    🚄 高铁{train_number}次列车时刻表

                    列车信息：
                    - 车次：{train_number}次
                    - 列车类型：高速动车组
                    - 运行区段：北京南 → 上海虹桥
                    - 全程运行时间：约4小时30分钟

                    主要站点时刻表：
                    1. 北京南站    出发: 08:00
                    2. 天津西站    到达: 08:30  出发: 08:32
                    3. 济南西站    到达: 09:45  出发: 09:47
                    4. 南京南站    到达: 11:15  出发: 11:17
                    5. 上海虹桥站  到达: 12:30

                    注意事项：
                    - 请提前30分钟到站检票
                    - 列车正点率98%以上
                    - 支持二代身份证直接刷卡进站
                    - 车票预售期为15天

                    如需实时信息，请关注铁路12306官方APP。
                    """
                    self.save_mcp(query, mock_schedule, "train_schedule")
                    return mock_schedule
                except Exception as e:
                    return f"高铁{train_number}次列车时刻表查询失败：{e}"

            else:
                # 通用知识查询
                mock_knowledge = f"""
                关于"{query}"的参考信息：

                这是一个通用的查询请求。系统已经分析了您的需求：
                - 查询内容: {query}
                - 建议: 请提供更具体的信息以获得更好的帮助

                如果您需要编程帮助、数据查询或网页分析，请详细描述您的需求。
                """
                self.save_mcp(query, mock_knowledge, "general")
                return mock_knowledge

        except Exception as e:
            print(f"远程MCP查询失败: {e}")
            return None

    def _handle_at_query(self, query):
        """处理@查询的专用方法"""
        try:
            query_lower = query.lower()

            # @web - 网页相关查询
            if query_lower.startswith('web ') or '网页' in query_lower or '网站' in query_lower:
                search_term = query.replace('web ', '').replace('网页', '').replace('网站', '').strip()
                
                # 特殊处理：机票价格查询
                if any(word in search_term for word in ['机票', '航班', '机票价格']):
                    return self._handle_flight_price_query(search_term, query)
                
                # 特殊处理：热搜查询
                if any(word in search_term for word in ['热搜', '百度热搜', '微博热搜', '热门话题']):
                    return self._handle_trending_search_query(search_term, query)
                
                # 特殊处理：实时API查询
                if any(word in search_term for word in ['实时', 'API', '代码示例']):
                    return self._handle_api_code_query(search_term, query)
                
                try:
                    import requests
                    # 尝试直接访问URL
                    if search_term.startswith('http'):
                        response = requests.get(search_term, timeout=5)
                        if response.status_code == 200:
                            content = response.text[:1000]
                            result = f"📄 网页内容查询结果：\n\n{search_term}\n\n内容摘要：\n{content[:500]}..."
                            self.save_mcp(f"@{query}", result, "web_content")
                            return result
                    else:
                        # 搜索相关网页
                        result = f"🔍 网页搜索结果：\n\n关于'{search_term}'的网页信息\n\n建议访问相关网站获取详细信息。"
                        self.save_mcp(f"@{query}", result, "web_search")
                        return result
                except Exception as e:
                    return f"网页查询失败：{e}"

            # @api - API相关查询
            elif query_lower.startswith('api ') or 'api' in query_lower:
                api_term = query.replace('api ', '').strip()
                result = (
                    f"🔌 API查询结果：\n\n"
                    f"关于'{api_term}'的API信息\n\n"
                    "API文档和使用指南：\n"
                    "- RESTful API设计规范\n"
                    "- 认证方式：Bearer Token\n"
                    "- 请求格式：JSON\n"
                    "- 响应格式：JSON\n\n"
                    "如需具体API文档，请提供更多详细信息。"
                )
                self.save_mcp(f"@{query}", result, "api_info")
                return result

            # @code - 编程相关查询
            elif query_lower.startswith('code ') or any(word in query_lower for word in ['代码', '编程', '开发']):
                code_term = (
                    query.replace('code ', '')
                    .replace('代码', '')
                    .replace('编程', '')
                    .replace('开发', '')
                    .strip()
                )
                result = (
                    f"💻 编程查询结果：\n\n"
                    f"关于'{code_term}'的编程信息\n\n"
                    "代码示例：\n"
                    "```python\n"
                    "# 这是一个示例函数\n"
                    "def example_function():\n"
                    "    return 'Hello, World!'\n\n"
                    "# 使用示例\n"
                    "result = example_function()\n"
                    "print(result)\n"
                    "```\n\n"
                    "建议：\n"
                    "1. 查看官方文档\n"
                    "2. 参考最佳实践\n"
                    "3. 进行单元测试"
                )
                self.save_mcp(f"@{query}", result, "code_example")
                return result

            # @data - 数据相关查询
            elif query_lower.startswith('data ') or '数据' in query_lower:
                data_term = query.replace('data ', '').replace('数据', '').strip()
                result = (
                    f"📊 数据查询结果：\n\n"
                    f"关于'{data_term}'的数据信息\n\n"
                    "数据分析建议：\n"
                    "- 数据清洗和预处理\n"
                    "- 特征工程\n"
                    "- 模型选择\n"
                    "- 性能评估\n\n"
                    "常用工具：pandas, numpy, scikit-learn"
                )
                self.save_mcp(f"@{query}", result, "data_analysis")
                return result

            # @train - 列车查询（保持原有功能）
            elif any(word in query_lower for word in ['高铁', '火车', '列车', '车次']):
                import re
                train_match = re.search(r'(\d+)', query)
                if train_match:
                    train_number = train_match.group(1)
                    result = (
                        f"\n🚄 高铁{train_number}次列车时刻表\n\n"
                        "列车信息：\n"
                        f"- 车次：{train_number}次\n"
                        "- 列车类型：高速动车组\n"
                        "- 运行区段：北京南 → 上海虹桥\n"
                        "- 全程运行时间：约4小时30分钟\n\n"
                        "主要站点时刻表：\n"
                        "1. 北京南站    出发: 08:00\n"
                        "2. 天津西站    到达: 08:30  出发: 08:32\n"
                        "3. 济南西站    到达: 09:45  出发: 09:47\n"
                        "4. 南京南站    到达: 11:15  出发: 11:17\n"
                        "5. 上海虹桥站  到达: 12:30\n\n"
                        "注意事项：\n"
                        "- 请提前30分钟到站检票\n"
                        "- 列车正点率98%以上\n"
                        "- 支持二代身份证直接刷卡进站\n"
                        "- 车票预售期为15天\n\n"
                        "如需实时信息，请关注铁路12306官方APP。\n"
                    )
                    self.save_mcp(f"@{query}", result, "train_schedule")
                    return result

            # @help - 帮助信息
            elif query_lower in ['help', '帮助', '?']:
                result = (
                    "🆘 MCP查询帮助\n\n"
                    "支持的@查询类型：\n"
                    "@web <关键词>     - 网页搜索和内容查询\n"
                    "@api <关键词>     - API相关信息查询\n"
                    "@code <关键词>    - 编程代码示例查询\n"
                    "@data <关键词>    - 数据分析相关查询\n"
                    "@train <车次>     - 列车时刻表查询\n"
                    "@help             - 显示此帮助信息\n\n"
                    "使用示例：\n"
                    "@web python教程\n"
                    "@api RESTful设计\n"
                    "@code 机器学习算法\n"
                    "@data 数据可视化\n"
                    "@train G902\n\n"
                    "注意：@查询会明确通过MCP服务处理，不使用数据库插件。"
                )
                return result

            # 默认@查询处理
            else:
                result = (
                    f"🔍 通用@查询结果：\n\n"
                    f"关于'{query}'的信息\n\n"
                    "这是一个通过MCP服务处理的查询。\n"
                    "建议：\n"
                    "- 提供更具体的关键字\n"
                    "- 使用特定类型前缀（如@web, @code等）\n"
                    "- 查看@help获取更多帮助"
                )
                self.save_mcp(f"@{query}", result, "general_at_query")
                return result

        except Exception as e:
            error_result = f"@查询处理失败：{e}"
            print(error_result)
            return error_result

    def _handle_flight_price_query(self, search_term, original_query):
        """处理机票价格查询"""
        try:
            # 解析查询中的关键信息
            import re
            
            # 提取日期信息
            date_match = re.search(r'(\d{1,2}月\d{1,2}日|\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2})', search_term)
            date_str = date_match.group(1) if date_match else "未指定日期"
            
            # 提取出发地和目的地
            cities = []
            for word in ['北京', '上海', '广州', '深圳', '东京', '纽约', '伦敦', '巴黎']:
                if word in search_term:
                    cities.append(word)
            
            departure = cities[0] if len(cities) > 0 else "未知"
            destination = cities[1] if len(cities) > 1 else "未知"
            
            # 生成实用的机票查询指导
            result = f"""✈️ 机票价格查询助手

📋 查询信息：
• 出发地：{departure}
• 目的地：{destination} 
• 日期：{date_str}

🔍 建议查询渠道：
1. **官方渠道**：
   - 各航空公司官网
   - 机场官方预订系统
   
2. **在线平台**：
   - 携程 (ctrip.com)
   - 去哪儿 (qunar.com)
   - 飞猪 (fliggy.com)
   - Google Flights
   - Kayak.com

3. **查询要点**：
   - 提前1-2个月预订通常价格更优
   - 比较多个平台价格
   - 关注航空公司促销活动
   - 考虑中转航班降低成本

💡 **实时代码示例**（Python）：
```python
import requests
from datetime import datetime

def search_flight_price(departure, destination, date):
    '''
    机票价格查询代码模板
    注意：实际使用需要API密钥
    '''
    # 示例：使用携程API（需要API密钥）
    api_url = "https://api.example.com/flights/search"
    params = {{
        'from': departure,
        'to': destination,
        'date': date,
        'api_key': 'YOUR_API_KEY'
    }}
    
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('flights', [])
    except Exception as e:
        print(f"查询失败：{{e}}")
    
    return None

# 使用示例
flights = search_flight_price('{departure}', '{destination}', '{date_str}')
```

⚠️ **重要提醒**：
- 以上代码为示例，实际使用需要申请相应平台的API密钥
- 建议直接访问官方网站获取最准确的实时价格
- 机票价格实时变动，以实际支付时价格为准
"""
            
            self.save_mcp(f"@{original_query}", result, "flight_price_guide")
            return result
            
        except Exception as e:
            return f"机票价格查询处理失败：{e}"

    def _handle_api_code_query(self, search_term, original_query):
        """处理API代码查询"""
        try:
            # 根据查询内容提供相应的API代码示例
            if '机票' in search_term or '航班' in search_term:
                result = """🛠️ 机票价格API查询代码

📝 **通用机票查询API代码框架**：

```python
import requests
import json
from datetime import datetime, timedelta

class FlightPriceAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_urls = {
            'amadeus': 'https://api.amadeus.com/v2/shopping/flight-offers',
            'skyscanner': 'https://rapidapi.p.rapidapi.com/flights/auto-complete',
            'example': 'https://api.example-travel.com/flights'
        }
    
    def search_flights(self, departure_city, arrival_city, departure_date, return_date=None):
        \"\"\"
        搜索机票价格
        
        Args:
            departure_city: 出发城市 (如 'BJS' 或 'Beijing')
            arrival_city: 到达城市 (如 'NRT' 或 'Tokyo')
            departure_date: 出发日期 (格式: 'YYYY-MM-DD')
            return_date: 返程日期 (可选)
        
        Returns:
            dict: 航班信息和价格
        \"\"\"
        
        params = {
            'origin': departure_city,
            'destination': arrival_city,
            'departureDate': departure_date,
            'adults': 1,
            'currency': 'CNY'
        }
        
        if return_date:
            params['returnDate'] = return_date
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                self.base_urls['amadeus'], 
                params=params, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return self.parse_flight_data(response.json())
            else:
                return {'error': f'API请求失败: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'error': f'网络请求失败: {str(e)}'}
    
    def parse_flight_data(self, raw_data):
        \"\"\"解析API返回的航班数据\"\"\"
        flights = []
        
        for offer in raw_data.get('data', []):
            flight_info = {
                'airline': offer['segments'][0]['airline']['name'],
                'flight_number': offer['segments'][0]['number'],
                'departure_time': offer['segments'][0]['departure']['time'],
                'arrival_time': offer['segments'][0]['arrival']['time'],
                'duration': offer['segments'][0]['duration'],
                'price': {
                    'amount': offer['price']['total'],
                    'currency': offer['price']['currency']
                },
                'booking_url': offer.get('booking_url', '')
            }
            flights.append(flight_info)
        
        return {'flights': flights, 'total_count': len(flights)}
    
    def get_cheapest_flight(self, departure_city, arrival_city, departure_date):
        \"\"\"获取最便宜的航班\"\"\"
        result = self.search_flights(departure_city, arrival_city, departure_date)
        
        if 'error' in result:
            return result
            
        flights = result.get('flights', [])
        if not flights:
            return {'error': '未找到航班信息'}
        
        # 按价格排序
        cheapest = min(flights, key=lambda x: float(x['price']['amount']))
        return cheapest

# 使用示例
if __name__ == "__main__":
    # 注意：需要申请实际的API密钥
    api = FlightPriceAPI(api_key='YOUR_API_KEY_HERE')
    
    # 查询北京到东京的航班
    result = api.search_flights('BJS', 'NRT', '2025-09-22')
    
    if 'error' not in result:
        print(f"找到 {result['total_count']} 个航班选项：")
        for i, flight in enumerate(result['flights'][:3], 1):
            print(f"{i}. {flight['airline']} {flight['flight_number']}")
            print(f"   价格: ¥{flight['price']['amount']}")
            print(f"   时间: {flight['departure_time']} - {flight['arrival_time']}")
            print(f"   飞行时长: {flight['duration']}")
            print()
    else:
        print(f"查询失败: {result['error']}")
```

🔑 **API密钥申请渠道**：
1. **Amadeus API** - 专业航空数据API
2. **Skyscanner API** - 通过RapidAPI平台
3. **Google Travel API** - 需要Google Cloud账号
4. **各航空公司开放API** - 查看各航司开发者页面

⚠️ **注意事项**：
- 大部分真实API需要付费或有访问限制
- 请求频率通常有限制，需要注意Rate Limiting  
- 生产环境需要错误处理和重试机制
- 价格可能有延迟，以官方网站为准
"""
            else:
                result = f"📝 API代码查询结果：\n\n关于'{search_term}'的API代码示例\n\n请提供更具体的API类型以获得详细的代码示例。"
            
            self.save_mcp(f"@{original_query}", result, "api_code_example")
            return result
            
        except Exception as e:
            return f"API代码查询处理失败：{e}"

    def _handle_trending_search_query(self, search_term, original_query):
        """处理热搜查询的专用方法"""
        try:
            # 检测查询类型
            query_lower = search_term.lower()
            
            if '百度' in query_lower:
                platform = "百度"
                result = self._get_baidu_trending_code()
            elif '微博' in query_lower:
                platform = "微博"
                result = self._get_weibo_trending_code()
            else:
                # 通用热搜查询，提供多平台代码
                platform = "多平台"
                result = self._get_general_trending_code()
            
            # 构建完整响应
            full_result = f"""🔥 {platform}热搜查询 - MCP学习结果

查询需求：{search_term}

{result}

⚠️ **重要说明**：
- 以上代码需要网络访问权限
- 实际网页结构可能变化，需要适时更新选择器
- 建议添加异常处理和重试机制
- 遵守网站robots.txt和使用条款

💡 **建议**：
1. 先在浏览器开发者工具中确认网页结构
2. 添加User-Agent避免被反爬虫检测
3. 实现缓存机制避免频繁请求
4. 考虑使用官方API（如有提供）"""
            
            self.save_mcp(f"@{original_query}", full_result, "trending_search_code")
            return full_result
            
        except Exception as e:
            return f"热搜查询处理失败: {e}"

    def _get_baidu_trending_code(self):
        """获取百度热搜爬取代码"""
        return '''💻 **百度热搜爬取代码示例**：

```python
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_baidu_hot_search(top_n=10):
    """
    获取百度热搜榜前N条
    """
    url = "https://top.baidu.com/board?tab=realtime"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找热搜条目（根据实际页面结构调整）
        hot_items = soup.find_all('div', class_='c-single-text-ellipsis')
        
        results = []
        for i, item in enumerate(hot_items[:top_n], 1):
            title = item.get_text().strip()
            if title:
                results.append({
                    'rank': i,
                    'title': title,
                    'source': '百度热搜',
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return results
        
    except Exception as e:
        print(f"百度热搜获取失败: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    hot_search = get_baidu_hot_search(10)
    
    print("📈 百度热搜榜 TOP 10:")
    print("=" * 50)
    
    for item in hot_search:
        print(f"{item['rank']:2d}. {item['title']}")
    
    print("=" * 50)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
```'''

    def _get_weibo_trending_code(self):
        """获取微博热搜爬取代码"""
        return '''💻 **微博热搜爬取代码示例**：

```python
import requests
import json
from datetime import datetime

def get_weibo_hot_search(top_n=10):
    """
    获取微博热搜榜前N条
    """
    # 微博热搜API（可能需要登录验证）
    url = "https://weibo.com/ajax/side/hotSearch"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://weibo.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        if 'data' in data and 'realtime' in data['data']:
            for i, item in enumerate(data['data']['realtime'][:top_n], 1):
                results.append({
                    'rank': i,
                    'title': item.get('note', ''),
                    'hot_score': item.get('num', 0),
                    'category': item.get('category', ''),
                    'source': '微博热搜',
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return results
        
    except Exception as e:
        print(f"微博热搜获取失败: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    hot_search = get_weibo_hot_search(10)
    
    print("🔥 微博热搜榜 TOP 10:")
    print("=" * 50)
    
    for item in hot_search:
        hot_score = f" (热度: {item['hot_score']})" if item['hot_score'] else ""
        category = f" [{item['category']}]" if item['category'] else ""
        print(f"{item['rank']:2d}. {item['title']}{hot_score}{category}")
    
    print("=" * 50)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
```'''

    def _get_general_trending_code(self):
        """获取通用热搜爬取代码（多平台）"""
        return '''💻 **多平台热搜聚合代码示例**：

```python
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import asyncio
import aiohttp

class TrendingAggregator:
    """多平台热搜聚合器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def get_baidu_trending(self, session, top_n=10):
        """获取百度热搜"""
        try:
            url = "https://top.baidu.com/board?tab=realtime"
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                items = soup.find_all('div', class_='c-single-text-ellipsis')
                results = []
                
                for i, item in enumerate(items[:top_n], 1):
                    title = item.get_text().strip()
                    if title:
                        results.append({
                            'rank': i,
                            'title': title,
                            'platform': '百度',
                            'hot_score': None
                        })
                
                return results
        except Exception as e:
            print(f"百度热搜获取失败: {e}")
            return []
    
    async def get_all_trending(self, top_n=10):
        """获取所有平台热搜"""
        async with aiohttp.ClientSession() as session:
            # 并发获取各平台热搜
            tasks = [
                self.get_baidu_trending(session, top_n),
                # 可以添加更多平台
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            all_trending = []
            for platform_result in results:
                if isinstance(platform_result, list):
                    all_trending.extend(platform_result)
            
            return all_trending

# 使用示例
async def main():
    aggregator = TrendingAggregator()
    trending_data = await aggregator.get_all_trending(10)
    
    print("🔥 多平台热搜聚合结果:")
    print("=" * 60)
    
    # 按平台分组显示
    platforms = {}
    for item in trending_data:
        platform = item['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(item)
    
    for platform, items in platforms.items():
        print(f"\n📱 {platform}热搜:")
        print("-" * 30)
        for item in items:
            print(f"{item['rank']:2d}. {item['title']}")
    
    print("\n" + "=" * 60)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```'''
