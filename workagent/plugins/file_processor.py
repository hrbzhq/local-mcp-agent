import os
import json
import csv
import pandas as pd
from typing import Dict, Any, List, Union
import logging
from pathlib import Path
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.plugin_manager import PluginInterface

# 可选依赖
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    PyPDF2 = None

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    docx = None

class FileProcessorPlugin(PluginInterface):
    """文件处理插件"""

    @property
    def name(self) -> str:
        return "file_processor"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "多格式文件读取和处理插件"

    def __init__(self):
        self.supported_formats = {
            '.txt': self._read_text,
            '.json': self._read_json,
            '.csv': self._read_csv,
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.md': self._read_markdown
        }

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.max_file_size = config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
            self.allowed_extensions = config.get('allowed_extensions', list(self.supported_formats.keys()))
            logging.info("FileProcessorPlugin 初始化成功")
            return True
        except Exception as e:
            logging.error(f"FileProcessorPlugin 初始化失败: {e}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行文件处理"""
        action = kwargs.get('action', 'read')

        if action == 'read':
            return self.read_file(**kwargs)
        elif action == 'analyze':
            return self.analyze_file(**kwargs)
        elif action == 'convert':
            return self.convert_file(**kwargs)
        elif action == 'search':
            return self.search_in_file(**kwargs)
        else:
            return {"error": f"不支持的操作: {action}"}

    def read_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """读取文件内容"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}

            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {"error": f"文件过大: {file_size} bytes (最大允许: {self.max_file_size} bytes)"}

            file_ext = Path(file_path).suffix.lower()

            if file_ext not in self.allowed_extensions:
                return {"error": f"不支持的文件格式: {file_ext}"}

            if file_ext in self.supported_formats:
                content = self.supported_formats[file_ext](file_path)
                return {
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_type": file_ext,
                    "content": content,
                    "status": "success"
                }
            else:
                return {"error": f"不支持的文件格式: {file_ext}"}

        except Exception as e:
            logging.error(f"读取文件失败 {file_path}: {e}")
            return {"error": str(e)}

    def analyze_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """分析文件内容"""
        try:
            result = self.read_file(file_path)
            if "error" in result:
                return result

            content = result["content"]
            analysis = {
                "file_info": {
                    "path": result["file_path"],
                    "size": result["file_size"],
                    "type": result["file_type"]
                },
                "statistics": {}
            }

            if isinstance(content, str):
                analysis["statistics"] = {
                    "character_count": len(content),
                    "word_count": len(content.split()),
                    "line_count": len(content.split('\n')),
                    "paragraph_count": len([p for p in content.split('\n\n') if p.strip()])
                }
            elif isinstance(content, list):
                analysis["statistics"] = {
                    "row_count": len(content),
                    "column_count": len(content[0]) if content else 0
                }
            elif isinstance(content, dict):
                analysis["statistics"] = {
                    "key_count": len(content),
                    "nested_levels": self._calculate_nested_levels(content)
                }

            return analysis

        except Exception as e:
            logging.error(f"分析文件失败 {file_path}: {e}")
            return {"error": str(e)}

    def search_in_file(self, file_path: str, query: str, **kwargs) -> Dict[str, Any]:
        """在文件中搜索内容"""
        try:
            result = self.read_file(file_path)
            if "error" in result:
                return result

            content = result["content"]
            matches = []

            if isinstance(content, str):
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        matches.append({
                            "line_number": i + 1,
                            "content": line.strip(),
                            "position": line.lower().find(query.lower())
                        })
            elif isinstance(content, list):
                for i, row in enumerate(content):
                    row_str = str(row)
                    if query.lower() in row_str.lower():
                        matches.append({
                            "row_number": i + 1,
                            "content": row_str,
                            "position": row_str.lower().find(query.lower())
                        })

            return {
                "query": query,
                "total_matches": len(matches),
                "matches": matches[:50]  # 限制结果数量
            }

        except Exception as e:
            logging.error(f"搜索文件失败 {file_path}: {e}")
            return {"error": str(e)}

    def convert_file(self, file_path: str, target_format: str, **kwargs) -> Dict[str, Any]:
        """转换文件格式"""
        try:
            result = self.read_file(file_path)
            if "error" in result:
                return result

            content = result["content"]
            converted_content = None

            # 简单的格式转换逻辑
            if target_format == 'json':
                if isinstance(content, str):
                    converted_content = {"text": content}
                elif isinstance(content, list):
                    converted_content = {"data": content}
                else:
                    converted_content = content
            elif target_format == 'txt':
                if isinstance(content, (list, dict)):
                    converted_content = json.dumps(content, indent=2, ensure_ascii=False)
                else:
                    converted_content = str(content)

            return {
                "original_file": file_path,
                "target_format": target_format,
                "converted_content": converted_content,
                "status": "success"
            }

        except Exception as e:
            logging.error(f"转换文件失败 {file_path}: {e}")
            return {"error": str(e)}

    def _read_text(self, file_path: str) -> str:
        """读取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_json(self, file_path: str) -> Dict[str, Any]:
        """读取JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """读取CSV文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            return "PDF处理需要安装PyPDF2库"

    def _read_docx(self, file_path: str) -> str:
        """读取Word文档"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            return "Word文档处理需要安装python-docx库"

    def _read_markdown(self, file_path: str) -> str:
        """读取Markdown文件"""
        return self._read_text(file_path)

    def _calculate_nested_levels(self, data: Any, level: int = 0) -> int:
        """计算嵌套层数"""
        if isinstance(data, dict):
            if not data:
                return level
            return max(self._calculate_nested_levels(v, level + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return level
            return max(self._calculate_nested_levels(item, level + 1) for item in data)
        else:
            return level

    def cleanup(self):
        """清理资源"""
        logging.info("FileProcessorPlugin 清理完成")
