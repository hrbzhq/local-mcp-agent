import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.plugin_manager import PluginInterface

class NotificationPlugin(PluginInterface):
    """通知插件"""

    @property
    def name(self) -> str:
        return "notification"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "多渠道通知插件（邮件、Webhook、桌面通知）"

    def __init__(self):
        self.email_config = {}
        self.webhook_config = {}
        self.notification_history = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            # 邮件配置
            self.email_config = config.get('email', {})
            self.email_server = self.email_config.get('server', 'smtp.gmail.com')
            self.email_port = self.email_config.get('port', 587)
            self.email_username = self.email_config.get('username', '')
            self.email_password = self.email_config.get('password', '')

            # Webhook配置
            self.webhook_config = config.get('webhook', {})
            self.webhook_urls = self.webhook_config.get('urls', [])

            # 通知配置
            self.enable_desktop = config.get('enable_desktop', True)
            self.enable_email = config.get('enable_email', False)
            self.enable_webhook = config.get('enable_webhook', False)

            logging.info("NotificationPlugin 初始化成功")
            return True
        except Exception as e:
            logging.error(f"NotificationPlugin 初始化失败: {e}")
            return False

    def execute(self, *args, **kwargs) -> Any:
        """执行通知"""
        action = kwargs.get('action', 'send')

        if action == 'send':
            return self.send_notification(**kwargs)
        elif action == 'email':
            return self.send_email(**kwargs)
        elif action == 'webhook':
            return self.send_webhook(**kwargs)
        elif action == 'desktop':
            return self.send_desktop_notification(**kwargs)
        elif action == 'history':
            return self.get_notification_history(**kwargs)
        else:
            return {"error": f"不支持的操作: {action}"}

    def send_notification(self, title: str, message: str, channels: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """发送多渠道通知"""
        if channels is None:
            channels = []
            if self.enable_desktop:
                channels.append('desktop')
            if self.enable_email:
                channels.append('email')
            if self.enable_webhook:
                channels.append('webhook')

        results = {}
        timestamp = datetime.now().isoformat()

        # 记录通知历史
        notification_record = {
            'timestamp': timestamp,
            'title': title,
            'message': message,
            'channels': channels
        }

        for channel in channels:
            try:
                if channel == 'desktop':
                    result = self.send_desktop_notification(title, message)
                elif channel == 'email':
                    result = self.send_email(title, message, **kwargs)
                elif channel == 'webhook':
                    result = self.send_webhook(title, message, **kwargs)
                else:
                    result = {"error": f"不支持的通知渠道: {channel}"}

                results[channel] = result
                notification_record[f'{channel}_result'] = result

            except Exception as e:
                error_result = {"error": str(e)}
                results[channel] = error_result
                notification_record[f'{channel}_result'] = error_result

        self.notification_history.append(notification_record)

        # 只保留最近100条记录
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]

        return {
            "status": "completed",
            "timestamp": timestamp,
            "channels_attempted": channels,
            "results": results
        }

    def send_email(self, subject: str, body: str, recipients: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """发送邮件通知"""
        try:
            if not self.email_username or not self.email_password:
                return {"error": "邮件配置不完整"}

            if not recipients:
                recipients = self.email_config.get('default_recipients', [])

            if not recipients:
                return {"error": "未指定收件人"}

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # 发送邮件
            server = smtplib.SMTP(self.email_server, self.email_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_username, recipients, text)
            server.quit()

            return {
                "status": "success",
                "recipients": recipients,
                "subject": subject
            }

        except Exception as e:
            logging.error(f"发送邮件失败: {e}")
            return {"error": str(e)}

    def send_webhook(self, title: str, message: str, **kwargs) -> Dict[str, Any]:
        """发送Webhook通知"""
        try:
            if not self.webhook_urls:
                return {"error": "未配置Webhook URL"}

            payload = {
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "AgentSystem"
            }

            results = []
            for url in self.webhook_urls:
                try:
                    response = requests.post(
                        url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )

                    results.append({
                        "url": url,
                        "status_code": response.status_code,
                        "success": response.status_code < 400
                    })

                except Exception as e:
                    results.append({
                        "url": url,
                        "error": str(e),
                        "success": False
                    })

            success_count = sum(1 for r in results if r.get('success', False))

            return {
                "status": "completed",
                "total_webhooks": len(self.webhook_urls),
                "successful": success_count,
                "results": results
            }

        except Exception as e:
            logging.error(f"发送Webhook失败: {e}")
            return {"error": str(e)}

    def send_desktop_notification(self, title: str, message: str, **kwargs) -> Dict[str, Any]:
        """发送桌面通知"""
        try:
            # 使用系统原生通知
            import platform
            system = platform.system()

            if system == "Windows":
                # Windows通知
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            elif system == "Darwin":  # macOS
                import subprocess
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
            elif system == "Linux":
                import subprocess
                subprocess.run([
                    "notify-send", title, message
                ])
            else:
                logging.warning(f"不支持的操作系统: {system}")
                return {"error": f"不支持的操作系统: {system}"}

            return {
                "status": "success",
                "system": system,
                "title": title,
                "message": message[:100] + "..." if len(message) > 100 else message
            }

        except ImportError as e:
            return {"error": f"缺少必要的库: {e}"}
        except Exception as e:
            logging.error(f"发送桌面通知失败: {e}")
            return {"error": str(e)}

    def get_notification_history(self, limit: int = 20, **kwargs) -> Dict[str, Any]:
        """获取通知历史"""
        try:
            history = self.notification_history[-limit:] if limit > 0 else self.notification_history

            return {
                "status": "success",
                "total_count": len(self.notification_history),
                "returned_count": len(history),
                "history": history
            }

        except Exception as e:
            logging.error(f"获取通知历史失败: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """清理资源"""
        self.notification_history.clear()
        logging.info("NotificationPlugin 清理完成")
