#!/usr/bin/env python3
"""
协作AI示例 - 多模型协作解决复杂问题
演示如何让多个AI模型协作处理复杂任务
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional

# 配置
BASE_URL = "http://localhost:8000"

class CollaborativeAI:
    """协作AI客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 验证连接
        if not self._check_connection():
            raise ConnectionError(f"无法连接到MCP服务器: {base_url}")
    
    def _check_connection(self) -> bool:
        """检查服务器连接"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.RequestException:
            return []
    
    def collaborative_solve(
        self,
        problem: str,
        models: Optional[List[str]] = None,
        max_rounds: int = 3,
        strategy: str = "sequential"
    ) -> Dict[str, Any]:
        """
        协作解决问题
        
        Args:
            problem: 要解决的问题
            models: 参与协作的模型列表
            max_rounds: 最大协作轮数
            strategy: 协作策略 (sequential/parallel/consensus)
            
        Returns:
            协作结果字典
        """
        if models is None:
            # 默认使用推荐的模型组合
            available = self.get_available_models()
            models = self._select_optimal_models(available, problem)
        
        try:
            response = self.session.post(
                f"{self.base_url}/mcp",
                json={
                    "name": "collaborative_chat",
                    "arguments": {
                        "input": problem,
                        "models": models,
                        "max_rounds": max_rounds,
                        "strategy": strategy
                    }
                },
                timeout=120  # 协作可能需要更长时间
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            return {
                "status": "error",
                "error": f"协作请求失败: {str(e)}"
            }
    
    def _select_optimal_models(self, available_models: List[str], problem: str) -> List[str]:
        """根据问题自动选择最优的模型组合"""
        problem_lower = problem.lower()
        
        # 编程相关问题
        if any(keyword in problem_lower for keyword in 
               ['代码', 'code', 'python', 'javascript', '编程', 'algorithm', '算法']):
            return [model for model in available_models 
                   if 'deepseek' in model or 'coder' in model][:2] + \
                   [model for model in available_models 
                   if 'qwen' in model][:1]
        
        # 设计和架构问题
        elif any(keyword in problem_lower for keyword in 
                ['设计', 'design', '架构', 'architecture', '系统', 'system']):
            return [model for model in available_models 
                   if 'qwen' in model][:1] + \
                   [model for model in available_models 
                   if 'deepseek' in model][:1]
        
        # 通用问题
        else:
            return available_models[:2] if len(available_models) >= 2 else available_models

def print_collaboration_result(result: Dict[str, Any]):
    """格式化打印协作结果"""
    print("\n" + "="*60)
    
    if result.get("status") == "error":
        print(f"❌ 协作失败: {result.get('error', '未知错误')}")
        return
    
    data = result.get("data", {})
    collaboration_summary = data.get("collaboration_summary", {})
    
    print("🤝 协作AI解决方案")
    print(f"⏱️  执行时间: {result.get('execution_time', 0):.2f}秒")
    
    # 参与模型
    if "participating_models" in collaboration_summary:
        models = collaboration_summary["participating_models"]
        print(f"🤖 参与模型: {', '.join(models)}")
    
    # 协作策略
    if "strategy" in collaboration_summary:
        strategy = collaboration_summary["strategy"]
        print(f"📋 协作策略: {strategy}")
    
    # 协作轮数
    if "rounds_completed" in collaboration_summary:
        rounds = collaboration_summary["rounds_completed"]
        print(f"🔄 完成轮数: {rounds}")
    
    # 最终结果
    if "final_output" in collaboration_summary:
        print(f"\n🎯 最终解决方案:")
        print("-" * 40)
        print(collaboration_summary["final_output"])
        print("-" * 40)
    
    # 各模型贡献
    if "contributions" in collaboration_summary:
        print(f"\n📊 各模型贡献:")
        for i, contrib in enumerate(collaboration_summary["contributions"], 1):
            print(f"\n{i}. {contrib.get('model', 'Unknown')}:")
            print(f"   📝 总结: {contrib.get('summary', '无总结')}")
            if 'output' in contrib:
                # 只显示前200字符
                output = contrib['output']
                if len(output) > 200:
                    output = output[:200] + "..."
                print(f"   💬 输出: {output}")

def demo_scenarios():
    """演示不同的协作场景"""
    scenarios = [
        {
            "name": "软件架构设计",
            "problem": "设计一个电商平台的微服务架构，包括用户服务、商品服务、订单服务和支付服务，考虑高并发和数据一致性",
            "models": None,  # 自动选择
            "strategy": "sequential"
        },
        {
            "name": "算法优化",
            "problem": "给出一个排序算法的多种实现方案，比较它们的时间复杂度和空间复杂度，并提供Python代码实现",
            "models": None,  # 自动选择
            "strategy": "parallel"
        },
        {
            "name": "技术决策",
            "problem": "评估React vs Vue.js vs Angular三个前端框架，从学习曲线、性能、生态系统和维护性四个维度进行对比",
            "models": None,  # 自动选择
            "strategy": "consensus"
        }
    ]
    
    return scenarios

def main():
    """主函数"""
    print("🤝 Local MCP Agent - 协作AI示例")
    print("让多个AI模型协作解决复杂问题")
    
    try:
        # 初始化协作AI
        ai = CollaborativeAI()
        print(f"✅ 成功连接到服务器: {BASE_URL}")
        
        # 获取可用模型
        models = ai.get_available_models()
        print(f"📋 可用模型: {', '.join(models)}")
        
        if len(models) < 2:
            print("⚠️  警告: 建议至少有2个模型以获得更好的协作效果")
        
    except ConnectionError as e:
        print(f"❌ {e}")
        return
    
    print("\n" + "="*60)
    print("选择模式:")
    print("1. 预设场景演示")
    print("2. 自定义问题")
    print("3. 交互式问题解决")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == "1":
        # 预设场景演示
        scenarios = demo_scenarios()
        
        print(f"\n🎬 开始演示 {len(scenarios)} 个场景...")
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*60}")
            print(f"📋 场景 {i}: {scenario['name']}")
            print(f"❓ 问题: {scenario['problem']}")
            
            # 开始协作
            print("\n🤔 AI模型协作中...")
            start_time = time.time()
            
            result = ai.collaborative_solve(
                problem=scenario["problem"],
                models=scenario["models"],
                strategy=scenario["strategy"],
                max_rounds=3
            )
            
            print_collaboration_result(result)
            
            total_time = time.time() - start_time
            print(f"\n⏱️  场景总耗时: {total_time:.2f}秒")
            
            if i < len(scenarios):
                input("\n按回车继续下一个场景...")
    
    elif choice == "2":
        # 自定义问题
        problem = input("\n📝 请输入您要解决的问题: ").strip()
        if not problem:
            print("❌ 问题不能为空")
            return
        
        # 选择模型
        print(f"\n可用模型: {', '.join(models)}")
        model_input = input("选择参与协作的模型 (用逗号分隔，回车使用自动选择): ").strip()
        
        selected_models = None
        if model_input:
            selected_models = [m.strip() for m in model_input.split(",")]
            # 验证模型是否存在
            invalid_models = [m for m in selected_models if m not in models]
            if invalid_models:
                print(f"⚠️  警告: 以下模型不存在: {', '.join(invalid_models)}")
                selected_models = [m for m in selected_models if m in models]
        
        # 选择策略
        strategy = input("\n协作策略 (sequential/parallel/consensus，回车默认sequential): ").strip()
        if not strategy:
            strategy = "sequential"
        
        # 最大轮数
        rounds_input = input("最大协作轮数 (1-10，回车默认3): ").strip()
        max_rounds = 3
        if rounds_input.isdigit():
            max_rounds = min(max(int(rounds_input), 1), 10)
        
        print("\n🤔 AI模型协作中...")
        result = ai.collaborative_solve(
            problem=problem,
            models=selected_models,
            strategy=strategy,
            max_rounds=max_rounds
        )
        
        print_collaboration_result(result)
    
    elif choice == "3":
        # 交互式模式
        print("\n🔄 进入交互式协作模式")
        print("输入 'quit' 退出")
        
        while True:
            try:
                problem = input("\n💭 请输入问题: ").strip()
                
                if not problem:
                    continue
                
                if problem.lower() in ['quit', 'exit', 'q']:
                    print("👋 退出交互模式")
                    break
                
                print("🤔 协作求解中...")
                result = ai.collaborative_solve(problem)
                print_collaboration_result(result)
                
            except KeyboardInterrupt:
                print("\n👋 程序被中断")
                break
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
