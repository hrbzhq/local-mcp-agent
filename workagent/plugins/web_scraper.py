import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.plugin_manager import PluginInterface

class WebScraperPlugin(PluginInterface):
    """网页抓取插件"""

    @property
    def name(self) -> str:
        return "web_scraper"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "网页内容抓取和分析插件"

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.session = requests.Session()
            self.session.headers.update(self.headers)

            # 设置超时时间
            self.timeout = config.get('timeout', 30)
            self.max_retries = config.get('max_retries', 3)

            logging.info("WebScraperPlugin 初始化成功")
            return True
        except Exception as e:
            logging.error(f"WebScraperPlugin 初始化失败: {e}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行网页抓取"""
        action = kwargs.get('action', 'scrape')

        if action == 'scrape':
            return self.scrape_page(**kwargs)
        elif action == 'extract_links':
            return self.extract_links(**kwargs)
        elif action == 'extract_text':
            return self.extract_text(**kwargs)
        else:
            return {"error": f"不支持的操作: {action}"}

    def scrape_page(self, url: str, **kwargs) -> Dict[str, Any]:
        """抓取网页内容"""
        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}: {response.reason}"}

            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取基本信息
            result = {
                "url": url,
                "status_code": response.status_code,
                "title": soup.title.string if soup.title else "",
                "meta_description": "",
                "headings": [],
                "links": [],
                "text_content": ""
            }

            # 提取meta描述
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                result["meta_description"] = meta_desc.get('content', '')

            # 提取标题
            for i in range(1, 7):
                headings = soup.find_all(f'h{i}')
                result["headings"].extend([h.get_text().strip() for h in headings])

            # 提取链接
            links = soup.find_all('a', href=True)
            result["links"] = [urljoin(url, link['href']) for link in links[:20]]  # 限制链接数量

            # 提取主要文本内容
            for script in soup(["script", "style"]):
                script.decompose()

            result["text_content"] = soup.get_text(separator='\n', strip=True)

            return result

        except Exception as e:
            logging.error(f"抓取页面失败 {url}: {e}")
            return {"error": str(e)}

    def extract_links(self, url: str, **kwargs) -> List[str]:
        """提取页面中的所有链接"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')

            links = []
            for a in soup.find_all('a', href=True):
                full_url = urljoin(url, a['href'])
                if self._is_valid_url(full_url):
                    links.append(full_url)

            return links

        except Exception as e:
            logging.error(f"提取链接失败 {url}: {e}")
            return []

    def extract_text(self, url: str, **kwargs) -> str:
        """提取页面的纯文本内容"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()

            # 获取文本
            text = soup.get_text(separator='\n', strip=True)

            # 清理文本
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)

        except Exception as e:
            logging.error(f"提取文本失败 {url}: {e}")
            return ""

    def _is_valid_url(self, url: str) -> bool:
        """检查URL是否有效"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme)
        except Exception as e:
            logging.debug(f"URL 解析失败: {e}")
            return False

    def cleanup(self):
        """清理资源"""
        if self.session:
            self.session.close()
        logging.info("WebScraperPlugin 清理完成")
