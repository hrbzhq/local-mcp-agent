import sqlite3
import json
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.plugin_manager import PluginInterface

class DatabasePlugin(PluginInterface):
    """数据库操作插件"""

    @property
    def name(self) -> str:
        return "database"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "SQLite数据库操作插件"

    def __init__(self):
        self.connection = None
        self.db_path = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.db_path = config.get('db_path', 'agent_data.db')

            # 连接到数据库
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

            # 创建必要的表
            self._create_tables()

            logging.info(f"DatabasePlugin 初始化成功，数据库: {self.db_path}")
            return True
        except Exception as e:
            logging.error(f"DatabasePlugin 初始化失败: {e}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行数据库操作"""
        action = kwargs.get('action', 'query')

        if action == 'query':
            return self.execute_query(**kwargs)
        elif action == 'insert':
            return self.insert_data(**kwargs)
        elif action == 'update':
            return self.update_data(**kwargs)
        elif action == 'delete':
            return self.delete_data(**kwargs)
        elif action == 'create_table':
            return self.create_table(**kwargs)
        elif action == 'backup':
            return self.backup_database(**kwargs)
        else:
            return {"error": f"不支持的操作: {action}"}

    def execute_query(self, sql: str, params: Optional[List[Any]] = None, **kwargs) -> Dict[str, Any]:
        """执行查询"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params or [])

            if sql.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]

                return {
                    "status": "success",
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results)
                }
            else:
                self.connection.commit()
                return {
                    "status": "success",
                    "affected_rows": cursor.rowcount
                }

        except Exception as e:
            logging.error(f"执行查询失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def insert_data(self, table: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """插入数据"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())

            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor = self.connection.cursor()
            cursor.execute(sql, values)
            self.connection.commit()

            return {
                "status": "success",
                "inserted_id": cursor.lastrowid,
                "affected_rows": cursor.rowcount
            }

        except Exception as e:
            logging.error(f"插入数据失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def update_data(self, table: str, data: Dict[str, Any], where: str, params: Optional[List[Any]] = None, **kwargs) -> Dict[str, Any]:
        """更新数据"""
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + (params or [])

            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

            cursor = self.connection.cursor()
            cursor.execute(sql, values)
            self.connection.commit()

            return {
                "status": "success",
                "affected_rows": cursor.rowcount
            }

        except Exception as e:
            logging.error(f"更新数据失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def delete_data(self, table: str, where: str, params: Optional[List[Any]] = None, **kwargs) -> Dict[str, Any]:
        """删除数据"""
        try:
            sql = f"DELETE FROM {table} WHERE {where}"

            cursor = self.connection.cursor()
            cursor.execute(sql, params or [])
            self.connection.commit()

            return {
                "status": "success",
                "affected_rows": cursor.rowcount
            }

        except Exception as e:
            logging.error(f"删除数据失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> Dict[str, Any]:
        """创建表"""
        try:
            columns = []
            for col_name, col_type in schema.items():
                if col_name.lower() == 'id':
                    columns.append(f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT")
                else:
                    columns.append(f"{col_name} {col_type}")

            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"

            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()

            return {
                "status": "success",
                "table": table_name,
                "schema": schema
            }

        except Exception as e:
            logging.error(f"创建表失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def backup_database(self, backup_path: str, **kwargs) -> Dict[str, Any]:
        """备份数据库"""
        try:
            # 使用SQLite的VACUUM INTO命令进行备份
            backup_sql = f"VACUUM INTO '{backup_path}'"

            cursor = self.connection.cursor()
            cursor.execute(backup_sql)
            self.connection.commit()

            # 检查备份文件大小
            import os
            backup_size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

            return {
                "status": "success",
                "backup_path": backup_path,
                "backup_size": backup_size
            }

        except Exception as e:
            logging.error(f"备份数据库失败: {e}")
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def _create_tables(self):
        """创建默认表结构"""
        try:
            # 任务历史表
            self.create_table('task_history', {
                'id': 'INTEGER PRIMARY KEY',
                'task_description': 'TEXT',
                'model_used': 'TEXT',
                'response': 'TEXT',
                'status': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })

            # 插件配置表
            self.create_table('plugin_configs', {
                'id': 'INTEGER PRIMARY KEY',
                'plugin_name': 'TEXT UNIQUE',
                'config': 'TEXT',
                'enabled': 'BOOLEAN DEFAULT 1',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })

            # 系统日志表
            self.create_table('system_logs', {
                'id': 'INTEGER PRIMARY KEY',
                'level': 'TEXT',
                'message': 'TEXT',
                'module': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })

            logging.info("默认表结构创建完成")

        except Exception as e:
            logging.error(f"创建默认表失败: {e}")

    def cleanup(self):
        """清理资源"""
        if self.connection:
            self.connection.close()
        logging.info("DatabasePlugin 清理完成")
