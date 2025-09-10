#!/usr/bin/env python3
"""
测试资源管理器优化时间窗口功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.resource_manager import ResourceManager
from datetime import datetime

def test_optimization_windows():
    """测试优化时间窗口功能"""
    rm = ResourceManager()

    print("=== 优化时间窗口配置测试 ===")
    windows = rm.get_optimization_windows()
    for opt_type, window in windows.items():
        print(f"{opt_type}: {window['start']:02d}:00 - {window['end']:02d}:00")

    print("\n=== 当前时间检查测试 ===")
    current_hour = datetime.now().hour
    print(f"当前时间: {current_hour}:00")

    for opt_type in windows.keys():
        is_window = rm._is_optimization_window(opt_type)
        status = "✓ 在窗口内" if is_window else "✗ 不在窗口内"
        print(f"{opt_type}: {status}")

    print("\n=== 时间窗口修改测试 ===")
    # 修改网络优化时间窗口为当前时间
    rm.set_optimization_window('network_optimization', current_hour, (current_hour + 1) % 24)
    is_window = rm._is_optimization_window('network_optimization')
    print(f"修改后网络优化窗口: {'✓ 在窗口内' if is_window else '✗ 不在窗口内'}")

if __name__ == "__main__":
    test_optimization_windows()
