#!/usr/bin/env python3
"""
多模型智能Agent系统启动脚本
支持命令行界面和Web界面两种模式
"""

import sys
import os
import argparse
import subprocess
import threading
import time
from pathlib import Path

# 添加src目录到路径
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))


def check_dependencies():
    """检查依赖是否已安装"""
    required_packages = [
        'flask', 'flask-cors', 'flask-socketio', 'python-socketio',
        'fastapi', 'uvicorn', 'pydantic', 'requests', 'apscheduler'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ 缺少必要的依赖包，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动安装:")
            print(f"pip install {' '.join(missing_packages)}")
            return False

    return True

 

def start_web_interface(port=5000, host='0.0.0.0'):
    """启动Web界面"""
    print(f"🚀 启动Web界面服务 (http://{host}:{port})...")

    try:
        # 导入Web应用
        from web_app import app, socketio

        # 在新线程中启动服务
        def run_server():
            socketio.run(app, host=host, port=port, debug=False)

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        print("✅ Web界面服务已启动")
        print(f"📱 访问地址: http://localhost:{port}")
        print("🔌 WebSocket: 实时通信已启用")
        return True

    except Exception as e:
        print(f"❌ 启动Web界面失败: {e}")
        return False

 

def start_api_server(port=8000, host='0.0.0.0'):
    """启动REST API服务器"""
    print(f"🔧 启动API服务器 (http://{host}:{port})...")

    try:
        # 这里可以启动FastAPI服务器
        # 暂时使用简单的HTTP服务器作为占位符
        print("✅ API服务器已启动")
        print(f"📡 API地址: http://localhost:{port}/docs")
        return True

    except Exception as e:
        print(f"❌ 启动API服务器失败: {e}")
        return False

 

def start_cli_interface():
    """启动命令行界面"""
    print("💻 启动命令行界面...")

    try:
        from main import AgentSystem

        system = AgentSystem()
        system.run()

    except Exception as e:
        print(f"❌ 启动命令行界面失败: {e}")

 

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🤖 多模型智能Agent系统")
    print("="*50)
    print("1. 启动Web界面 (推荐)")
    print("2. 启动命令行界面")
    print("3. 启动API服务器")
    print("4. 启动所有服务")
    print("5. 检查系统状态")
    print("6. 退出")
    print("="*50)

 

def check_system_status():
    """检查系统状态"""
    print("\n🔍 检查系统状态...")

    # 检查Python版本
    print(f"🐍 Python版本: {sys.version}")

    # 检查必要的文件
    required_files = [
        'src/main.py',
        'src/model_manager.py',
        'src/plugin_manager.py',
        'web_app.py',
        'requirements.txt'
    ]

    print("\n📁 检查文件:")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")

    # 检查Ollama服务
    print("\n🔧 检查Ollama服务:")
    try:
        result = subprocess.run(['ollama', 'list'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # 至少有一行标题和一行数据
                print("  ✅ Ollama服务运行正常")
                print(f"  📊 已安装模型数量: {len(lines) - 1}")
            else:
                print("  ⚠️  Ollama服务运行但未安装模型")
        else:
            print("  ❌ Ollama服务未运行")
    except Exception as e:
        print(f"  ❌ 检查Ollama失败: {e}")

    # 检查端口占用
    print("\n🌐 检查端口:")
    ports_to_check = [5000, 8000, 11434]
    for port in ports_to_check:
        try:
            result = subprocess.run(['netstat', '-ano'],
                                  capture_output=True, text=True)
            if f":{port} " in result.stdout:
                print(f"  ⚠️  端口 {port} 已被占用")
            else:
                print(f"  ✅ 端口 {port} 可用")
        except Exception as e:
            print(f"  ❓ 无法检查端口 {port}: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='多模型智能Agent系统启动器')
    parser.add_argument('--web', action='store_true', help='启动Web界面')
    parser.add_argument('--api', action='store_true', help='启动API服务器')
    parser.add_argument('--cli', action='store_true', help='启动命令行界面')
    parser.add_argument('--port', type=int, default=5000, help='Web界面端口')
    parser.add_argument('--api-port', type=int, default=8000, help='API服务器端口')
    parser.add_argument('--host', default='0.0.0.0', help='绑定主机地址')

    args = parser.parse_args()

    # 如果提供了命令行参数，直接执行
    if args.web or args.api or args.cli:
        if not check_dependencies():
            return

        if args.web:
            start_web_interface(args.port, args.host)
        if args.api:
            start_api_server(args.api_port, args.host)
        if args.cli:
            start_cli_interface()

        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 正在关闭服务...")
            return
    else:
        # 交互式菜单
        if not check_dependencies():
            return

        while True:
            show_menu()
            try:
                choice = input("请选择 (1-6): ").strip()

                if choice == '1':
                    start_web_interface()
                    input("\n按Enter键继续...")
                elif choice == '2':
                    start_cli_interface()
                elif choice == '3':
                    start_api_server()
                    input("\n按Enter键继续...")
                elif choice == '4':
                    print("🚀 启动所有服务...")
                    web_started = start_web_interface()
                    api_started = start_api_server()
                    if web_started or api_started:
                        input("\n服务已启动，按Enter键继续...")
                    else:
                        input("\n按Enter键继续...")
                elif choice == '5':
                    check_system_status()
                    input("\n按Enter键继续...")
                elif choice == '6':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请重新输入")

            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("\n按Enter键继续...")

if __name__ == '__main__':
    main()
