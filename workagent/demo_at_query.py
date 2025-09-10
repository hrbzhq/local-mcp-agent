#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@查询功能演示脚本
演示如何使用@查询功能进行不同类型的查询
"""

import requests
import json
import time

class AtQueryDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def send_query(self, query):
        """发送查询请求"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/tasks",
                json={"task": query, "model": "qwen3"},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def demo_help_query(self):
        """演示@help查询"""
        print("🔍 演示@help查询:")
        print("查询: @help")
        result = self.send_query("@help")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_web_query(self):
        """演示@web查询"""
        print("🌐 演示@web查询:")
        print("查询: @web python教程")
        result = self.send_query("@web python教程")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_code_query(self):
        """演示@code查询"""
        print("💻 演示@code查询:")
        print("查询: @code 快速排序算法")
        result = self.send_query("@code 快速排序算法")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_api_query(self):
        """演示@api查询"""
        print("🔌 演示@api查询:")
        print("查询: @api RESTful API设计")
        result = self.send_query("@api RESTful API设计")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_data_query(self):
        """演示@data查询"""
        print("📊 演示@data查询:")
        print("查询: @data 数据可视化工具")
        result = self.send_query("@data 数据可视化工具")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_train_query(self):
        """演示@train查询"""
        print("🚂 演示@train查询:")
        print("查询: @train G902")
        result = self.send_query("@train G902")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_general_at_query(self):
        """演示通用@查询"""
        print("🎯 演示通用@查询:")
        print("查询: @人工智能发展趋势")
        result = self.send_query("@人工智能发展趋势")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def demo_regular_query(self):
        """演示普通查询（对比）"""
        print("📝 演示普通查询（对比）:")
        print("查询: python教程")
        result = self.send_query("python教程")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(1)

    def run_all_demos(self):
        """运行所有演示"""
        print("=" * 60)
        print("🎯 @查询功能演示")
        print("=" * 60)
        print("请确保系统已启动 (python start.py --web)")
        print("-" * 60)

        # 检查系统状态
        try:
            status_response = self.session.get(f"{self.base_url}/api/status")
            if status_response.status_code == 200:
                print("✅ 系统状态正常")
            else:
                print("❌ 系统未启动或不可访问")
                return
        except Exception as e:
            print(f"❌ 无法连接到系统: {e}")
            return

        print("\n开始演示...\n")

        # 运行所有演示
        self.demo_help_query()
        self.demo_web_query()
        self.demo_code_query()
        self.demo_api_query()
        self.demo_data_query()
        self.demo_train_query()
        self.demo_general_at_query()
        self.demo_regular_query()

        print("=" * 60)
        print("🎉 演示完成！")
        print("=" * 60)
        print("📖 详细使用指南请查看: AT_QUERY_GUIDE.md")
        print("📚 系统文档请查看: README.md")

def main():
    """主函数"""
    demo = AtQueryDemo()

    print("选择演示模式:")
    print("1. 运行完整演示")
    print("2. 仅演示@help查询")
    print("3. 仅演示@web查询")
    print("4. 仅演示@code查询")
    print("5. 仅演示@api查询")
    print("6. 仅演示@data查询")
    print("7. 仅演示@train查询")

    choice = input("请选择 (1-7): ").strip()

    if choice == "1":
        demo.run_all_demos()
    elif choice == "2":
        demo.demo_help_query()
    elif choice == "3":
        demo.demo_web_query()
    elif choice == "4":
        demo.demo_code_query()
    elif choice == "5":
        demo.demo_api_query()
    elif choice == "6":
        demo.demo_data_query()
    elif choice == "7":
        demo.demo_train_query()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
