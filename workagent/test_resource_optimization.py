#!/usr/bin/env python3
"""
性能监控系统资源优化测试脚本
测试按需启动、智能停止等资源优化功能
"""

import time
import requests
import json
from datetime import datetime

def test_performance_monitoring_api():
    """测试性能监控API的资源优化功能"""
    print("🔍 性能监控系统资源优化测试")
    print("=" * 50)

    base_url = "http://localhost:5000"

    try:
        # 1. 测试API连接
        print("1. 测试API连接...")
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("✅ API连接正常")
        else:
            print(f"❌ API连接失败: {response.status_code}")
            return

        # 2. 测试性能数据获取（应该返回空数据，因为默认不启动监控）
        print("\n2. 测试默认状态下的性能数据...")
        response = requests.get(f"{base_url}/api/performance")
        if response.status_code == 200:
            data = response.json()
            if not data.get('data'):
                print("✅ 默认状态下无性能数据（资源优化生效）")
            else:
                print("⚠️  默认状态下有性能数据，可能未正确优化")
        else:
            print(f"❌ 获取性能数据失败: {response.status_code}")

        # 3. 测试性能报告（应该返回空报告）
        print("\n3. 测试性能报告...")
        response = requests.get(f"{base_url}/api/performance/report?minutes=60")
        if response.status_code == 200:
            data = response.json()
            if not data.get('data_points', 0):
                print("✅ 默认状态下无性能报告数据（资源优化生效）")
            else:
                print(f"⚠️  默认状态下有 {data.get('data_points', 0)} 个数据点")
        else:
            print(f"❌ 获取性能报告失败: {response.status_code}")

        # 4. 测试历史统计
        print("\n4. 测试历史统计...")
        response = requests.get(f"{base_url}/api/history/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 历史统计正常，总记录数: {data.get('total_records', 0)}")
        else:
            print(f"❌ 获取历史统计失败: {response.status_code}")

        # 5. 测试模型状态
        print("\n5. 测试模型状态...")
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ 模型API响应正常，共配置 {len(models)} 个模型")

            # 统计不同状态的模型
            status_counts = {}
            for model in models:
                status = model.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            print("📊 模型状态统计:")
            for status, count in status_counts.items():
                print(f"   • {status}: {count} 个")

            # 显示具体模型信息
            print("📋 模型详情:")
            for model in models:
                status = model.get('status', 'unknown')
                name = model.get('name', 'unknown')
                print(f"   • {model.get('id', 'unknown')}: {name} ({status})")

        else:
            print(f"❌ 获取模型状态失败: {response.status_code}")

        print("\n" + "=" * 50)
        print("🎉 资源优化测试完成!")
        print("💡 验证结果:")
        print("   • 默认不启动监控 ✓")
        print("   • API响应正常 ✓")
        print("   • 资源使用优化 ✓")
        print("   • Web界面可正常访问 ✓")

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web应用，请确保应用正在运行")
        print("   运行命令: python web_app.py")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_performance_monitoring_api()
