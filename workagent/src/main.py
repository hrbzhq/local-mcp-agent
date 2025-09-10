# flake8: noqa: E402
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from apscheduler.schedulers.background import BackgroundScheduler
from model_manager import ModelManager
from mcp_manager import MCPManager
from task_history_manager import TaskHistoryManager
from performance_monitor import PerformanceMonitor
from config_manager import ConfigManager
from plugin_manager import PluginManager
from data_visualizer import DataVisualizer
import logging
import time
from datetime import datetime

class AgentSystem:
    def __init__(self):
        self.model_manager = ModelManager()
        self.mcp_manager = MCPManager()
        self.task_history = TaskHistoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager()
        self.data_visualizer = DataVisualizer()
        self.scheduler = BackgroundScheduler()
        self.setup_logging()
        self.start_scheduler()
        self.running = True
        
        # 启动性能监控
        self.performance_monitor.start_monitoring()
        
        # 注册性能告警回调
        self.performance_monitor.add_alert_callback(self.handle_performance_alert)
    
    def setup_logging(self):
        logging.basicConfig(filename='logs/agent.log', level=logging.INFO)
        # 同时输出到控制台
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    
    def start_scheduler(self):
        # 定时任务：每小时检查 MCP 优化
        self.scheduler.add_job(self.optimize_mcp, 'interval', hours=1)
        self.scheduler.start()
        logging.info("定时任务已启动，每小时执行 MCP 优化")
    
    def optimize_mcp(self):
        """MCP递归优化算法"""
        logging.info("开始 MCP 递归优化...")

        try:
            # 1. 获取所有MCP模块的执行记录
            mcp_performance = self.analyze_mcp_performance()
            
            # 2. 使用DeepSeek-R1分析性能瓶颈
            for mcp_name, metrics in mcp_performance.items():
                if metrics['success_rate'] < 0.8:  # 成功率低于80%
                    logging.info("发现性能瓶颈: %s", mcp_name)

                    # 分析失败原因
                    analysis = self.model_manager.call_model(
                        'deepseek_r1',
                        f"""分析这个MCP模块的性能问题:
模块名称: {mcp_name}
性能指标: {metrics}
请提供优化建议和改进方案。""")

                    logging.info("MCP分析结果: %s", analysis)
                    
                    # 生成优化后的MCP
                    optimized_mcp = self.generate_optimized_mcp(mcp_name, analysis)
                    
                    if optimized_mcp:
                        # 保存优化版本
                        self.mcp_manager.save_mcp(f"{mcp_name}_optimized",
                                                optimized_mcp, 'optimized')
                        logging.info("MCP优化完成: %s", mcp_name)
            
            # 3. 自我评估优化效果
            self.evaluate_optimization_effect()
            
        except Exception as e:
            logging.error(f"MCP优化失败: {e}")
    
    def analyze_mcp_performance(self):
        """分析MCP性能指标"""
        # 这里应该从数据库或日志中获取实际性能数据
        # 暂时返回模拟数据
        return {
            'code_generator': {
                'success_rate': 0.85,
                'avg_execution_time': 2.3,
                'usage_count': 150,
                'error_types': ['timeout', 'syntax_error']
            },
            'web_search': {
                'success_rate': 0.92,
                'avg_execution_time': 1.8,
                'usage_count': 200,
                'error_types': ['network_error']
            },
            'data_analyzer': {
                'success_rate': 0.78,
                'avg_execution_time': 3.1,
                'usage_count': 80,
                'error_types': ['memory_error', 'data_format_error']
            }
        }
    
    def generate_optimized_mcp(self, mcp_name, analysis):
        """生成优化后的MCP"""
        # 使用Qwen2.5-coder生成优化代码
        optimization_prompt = f"""
基于以下分析结果，优化MCP模块 {mcp_name}:

分析结果: {analysis}

请生成优化后的MCP代码，重点解决性能瓶颈。
"""
        
        optimized_code = self.model_manager.call_model('qwen_coder', optimization_prompt)
        return optimized_code
    
    def process_task(self, task_input):
        """具体的任务处理逻辑"""
        logging.info(f"开始处理任务: {task_input}")
        start_time = time.time()
        
        try:
            # 1. 使用 Qwen3 解析任务类型和复杂度
            task_analysis = self.model_manager.call_model('qwen3', 
                f"""请分析这个任务，提取以下信息：
任务: {task_input}
请返回JSON格式：
{{
    "task_type": "编程|写作|分析|搜索|其他",
    "complexity": "简单|中等|复杂",
    "keywords": ["关键词1", "关键词2"],
    "estimated_time": "预估时间（分钟）",
    "required_skills": ["所需技能"]
}}""")
            logging.info(f"任务分析完成: {task_analysis}")
            
            # 2. 使用 Gemma3 快速判断是否需要MCP
            mcp_needed = self.model_manager.call_model('gemma3', 
                f"这个任务是否需要调用外部MCP模块？任务: {task_input} 回答是或否")
            logging.info(f"MCP需求判断: {mcp_needed}")
            
            # 3. 智能匹配MCP
            if "是" in str(mcp_needed).lower():
                mcp_name = self.find_best_mcp(task_input)
                mcp_content = self.mcp_manager.get_mcp(mcp_name)
                
                if mcp_content:
                    logging.info(f"找到本地MCP: {mcp_name}")
                    # 使用MCP执行任务
                    result = self.execute_with_mcp(task_input, mcp_content)
                else:
                    logging.info(f"本地未找到MCP: {mcp_name}，尝试远程查询...")
                    mcp_content = self.search_remote_mcp(task_input)
                    if mcp_content:
                        self.mcp_manager.save_mcp(mcp_name, mcp_content, 'remote')
                        result = self.execute_with_mcp(task_input, mcp_content)
                    else:
                        # 降级到直接模型处理
                        result = self.process_with_models(task_input)
            else:
                # 直接使用模型处理
                result = self.process_with_models(task_input)
            
            # 4. 记录执行结果和性能指标
            execution_time = time.time() - start_time
            self.record_task_result(task_input, result, execution_time)
            
            logging.info(f"任务处理完成，耗时: {execution_time:.2f}秒")
            return result
            
        except Exception as e:
            logging.error(f"任务处理失败: {e}")
            return f"任务处理失败: {str(e)}"
    
    def find_best_mcp(self, task_input):
        """智能匹配最佳MCP"""
        # 使用Qwen2.5-coder分析任务并匹配MCP
        analysis = self.model_manager.call_model('qwen_coder', 
            f"根据任务描述，推荐最合适的MCP模块名称: {task_input}")
        # 使用分析结果记录到日志以避免未使用变量警告
        logging.debug("find_best_mcp analysis: %s", analysis)
        
        # 简单的关键词匹配逻辑
        if "代码" in task_input or "编程" in task_input:
            return "code_generator"
        elif "搜索" in task_input or "查找" in task_input:
            return "web_search"
        elif "分析" in task_input or "数据" in task_input:
            return "data_analyzer"
        else:
            return "general_assistant"
    
    def execute_with_mcp(self, task_input, mcp_content):
        """使用MCP执行任务"""
        # 这里应该解析MCP内容并执行
        # 暂时模拟执行过程
        logging.info("使用MCP执行任务...")
        return f"MCP执行结果: {task_input} 已通过MCP处理"
    
    def process_with_models(self, task_input):
        """直接使用模型处理任务"""
        # 根据任务复杂度选择模型
        if len(task_input) < 50:  # 简单任务
            result = self.model_manager.call_model('gemma3', 
                f"请处理这个任务: {task_input}")
        elif "代码" in task_input:  # 编程任务
            result = self.model_manager.call_model('qwen_coder', 
                f"请编写代码解决: {task_input}")
        else:  # 复杂任务
            result = self.model_manager.call_model('deepseek_r1', 
                f"请深入分析并解决: {task_input}")
        
        return f"模型处理结果: {result}"
    
    def search_remote_mcp(self, task_input):
        """远程搜索MCP"""
        # 这里应该实现GitHub API或其他MCP仓库查询
        # 暂时返回模拟结果
        logging.info("正在远程搜索MCP...")
        return None  # 模拟未找到
    
    def record_task_result(self, task_input, result, execution_time):
        """记录任务执行结果"""
        # 可以保存到数据库或文件中
        logging.info(f"记录任务结果: 输入长度={len(task_input)}, 耗时={execution_time:.2f}s")
    
    def self_optimize(self):
        """工作工程自我优化"""
        logging.info("开始工作工程自我优化...")
        
        try:
            # 1. 分析系统性能指标
            system_metrics = self.collect_system_metrics()
            
            # 2. 识别改进机会
            improvement_areas = self.identify_improvements(system_metrics)
            
            # 3. 生成优化方案
            for area in improvement_areas:
                logging.info(f"优化领域: {area['name']}")
                
                # 使用DeepSeek-R1深入分析
                analysis = self.model_manager.call_model('deepseek_r1', 
                    f"""分析系统优化机会:
领域: {area['name']}
当前指标: {area['metrics']}
问题: {area['issues']}
请提供具体的改进方案。""")
                
                # 使用Qwen2.5-coder生成优化代码
                optimization_code = self.model_manager.call_model('qwen_coder', 
                    f"""基于分析结果生成优化代码:
{analysis}
请生成具体的代码改进方案。""")
                
                # 应用优化（这里是模拟）
                self.apply_optimization(area['name'], optimization_code)
                logging.info(f"优化应用完成: {area['name']}")
            
            # 4. 验证优化效果
            self.validate_optimizations()
            
        except Exception as e:
            logging.error(f"自我优化失败: {e}")
    
    def extract_task_type(self, analysis):
        """从分析结果中提取任务类型"""
        if analysis and "编程" in str(analysis):
            return "编程"
        elif analysis and "分析" in str(analysis):
            return "分析"
        elif analysis and "搜索" in str(analysis):
            return "搜索"
        else:
            return "其他"
    
    def extract_complexity(self, analysis):
        """从分析结果中提取复杂度"""
        if analysis and "复杂" in str(analysis):
            return "复杂"
        elif analysis and "中等" in str(analysis):
            return "中等"
        else:
            return "简单"
    
    def determine_model_used(self, task_input):
        """确定使用的模型"""
        if len(task_input) < 50:
            return "gemma3"
        elif "代码" in task_input:
            return "qwen_coder"
        else:
            return "qwen3"
    
    def handle_performance_alert(self, alert):
        """处理性能告警"""
        logging.warning(f"性能告警: {alert['message']}")
        # 可以在这里添加告警处理逻辑，如发送通知等
    
    def collect_system_metrics(self):
        """收集系统性能指标"""
        return {
            'task_processing': {
                'avg_response_time': 2.5,
                'success_rate': 0.88,
                'memory_usage': '150MB',
                'cpu_usage': '25%'
            },
            'model_management': {
                'model_load_time': 1.2,
                'inference_speed': 0.8,
                'error_rate': 0.05
            },
            'mcp_integration': {
                'cache_hit_rate': 0.75,
                'remote_query_time': 3.2,
                'module_count': 15
            }
        }
    
    def identify_improvements(self, metrics):
        """识别改进机会"""
        improvements = []
        
        # 分析任务处理性能
        if metrics['task_processing']['avg_response_time'] > 3.0:
            improvements.append({
                'name': 'task_processing_optimization',
                'metrics': metrics['task_processing'],
                'issues': ['响应时间过长', '资源利用率不高']
            })
        
        # 分析模型管理效率
        if metrics['model_management']['error_rate'] > 0.1:
            improvements.append({
                'name': 'model_error_handling',
                'metrics': metrics['model_management'],
                'issues': ['错误处理不完善', '模型切换效率低']
            })
        
        # 分析MCP集成效果
        if metrics['mcp_integration']['cache_hit_rate'] < 0.8:
            improvements.append({
                'name': 'mcp_cache_optimization',
                'metrics': metrics['mcp_integration'],
                'issues': ['缓存命中率低', '远程查询频繁']
            })
        
        return improvements
    
    def apply_optimization(self, area_name, optimization_code):
        """应用优化方案"""
        # 这里应该实际应用优化代码
        # 暂时记录优化日志
        logging.info(f"应用优化: {area_name}")
        logging.info(f"优化代码: {optimization_code}")
    
    def validate_optimizations(self):
        """验证优化效果"""
        logging.info("验证优化效果...")
        # 运行测试用例验证改进
        test_results = self.run_validation_tests()
        logging.info(f"验证结果: {test_results}")
    
    def run_validation_tests(self):
        """运行验证测试"""
        # 模拟测试结果
        return {
            'performance_improvement': '+15%',
            'error_rate_reduction': '-20%',
            'resource_efficiency': '+10%'
        }
    
    def model_dialogue(self, topic=None):
        """模型互问互答生成新需求"""
        logging.info("开始模型互问互答...")
        
        try:
            # 1. 确定对话主题
            if not topic:
                topic = self.generate_dialogue_topic()
            
            logging.info(f"对话主题: {topic}")
            
            # 2. 启动多模型对话
            dialogue_history = []
            insights = []
            
            # 轮流让不同模型提问和回答
            models = ['qwen3', 'gemma3', 'qwen_coder', 'deepseek_r1']
            
            for round_num in range(3):  # 3轮对话
                logging.info(f"开始第{round_num + 1}轮对话")
                
                for i, model_name in enumerate(models):
                    # 让当前模型基于历史对话提出问题或见解
                    context = f"主题: {topic}\n历史对话: {dialogue_history[-3:] if dialogue_history else '无'}"
                    
                    if i == 0:  # 第一个模型提出问题
                        response = self.model_manager.call_model(model_name, 
                            f"基于上下文，提出一个关于{topic}的问题:\n{context}")
                        dialogue_history.append(f"{model_name}提问: {response}")
                    else:  # 其他模型回答或提出见解
                        response = self.model_manager.call_model(model_name, 
                            f"回答上一个问题或分享关于{topic}的见解:\n{context}")
                        dialogue_history.append(f"{model_name}回答: {response}")
                    
                    # 提取有价值的见解
                    insight = self.extract_insight(response)
                    if insight:
                        insights.append({
                            'model': model_name,
                            'round': round_num + 1,
                            'insight': insight
                        })
            
            # 3. 分析对话结果，生成新需求
            new_requirements = self.generate_new_requirements(insights, topic)
            
            # 4. 保存对话记录和新需求
            self.save_dialogue_record(topic, dialogue_history, insights, new_requirements)
            
            logging.info(f"模型对话完成，生成了{len(new_requirements)}个新需求")
            return new_requirements
            
        except Exception as e:
            logging.error(f"模型对话失败: {e}")
            return []
    
    def generate_dialogue_topic(self):
        """生成对话主题"""
        # 从系统当前状态和历史任务中生成主题
        recent_topics = [
            "系统性能优化",
            "MCP模块改进", 
            "多模型协作效率",
            "任务处理智能化",
            "用户体验提升"
        ]
        
        # 使用模型选择最相关的主题
        topic_selection = self.model_manager.call_model('qwen3', 
            f"从这些主题中选择最需要讨论的一个: {recent_topics}")
        
        return topic_selection.strip() if topic_selection else "系统整体优化"
    
    def extract_insight(self, response):
        """从模型响应中提取有价值的见解"""
        # 使用简单关键词过滤提取见解
        insight_keywords = ['改进', '优化', '建议', '问题', '解决方案', '新功能', '效率']
        
        response_str = str(response).lower()
        for keyword in insight_keywords:
            if keyword in response_str:
                return str(response).strip()
        
        return None
    
    def generate_new_requirements(self, insights, topic):
        """基于对话见解生成新需求"""
        # 使用DeepSeek-R1分析见解并生成需求
        analysis_prompt = f"""
基于以下对话见解，生成新的系统需求:

主题: {topic}
见解列表: {insights}

请分析这些见解，识别有价值的改进机会，并生成具体的需求描述。
"""
        
        requirements_analysis = self.model_manager.call_model('deepseek_r1', analysis_prompt)
        
        # 解析生成的demand（这里简化处理）
        new_requirements = []
        if requirements_analysis:
            # 简单的需求提取逻辑
            lines = str(requirements_analysis).split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['需求', '功能', '改进', '优化']):
                    new_requirements.append(line.strip())
        
        return new_requirements[:5]  # 最多返回5个需求
    
    def save_dialogue_record(self, topic, history, insights, requirements):
        """保存对话记录"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'dialogue_history': history,
            'insights': insights,
            'new_requirements': requirements
        }

    # 保存到文件或数据库（占位），并记录概要信息
    logging.info("保存对话记录: %d条对话, %d个见解, %d个新需求",
             len(history), len(insights), len(requirements))
    # 记录完整记录以避免未使用变量警告，并便于调试
    logging.debug("保存对话记录详情: %s", record)

    def show_status(self):
        """显示系统状态"""
        print("\n" + "="*50)
        print("🤖 多模型智能 Agent 系统状态")
        print("="*50)
        print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔧 系统组件状态:")
        print("   ✅ 模型管理器: 已初始化")
        print("   ✅ MCP 管理器: 已初始化")
        print("   ✅ 任务历史管理器: 已初始化")
        print("   ✅ 性能监控器: 已初始化")
        print("   ✅ 配置管理器: 已初始化")
        print("   ✅ 插件管理器: 已初始化")
        print("   ✅ 数据可视化器: 已初始化")
        print("   ✅ 定时调度器: 运行中")
        print("   ✅ 日志系统: 运行中")
        print("\n📋 可用命令:")
        print("   task <任务描述>    - 处理任务")
        print("   status             - 显示系统状态")
        print("   optimize           - 执行自我优化")
        print("   dialogue           - 启动模型对话")
        print("   test               - 测试模型连接")
        print("   history            - 查看任务历史")
        print("   performance        - 查看性能报告")
        print("   config             - 查看配置信息")
        print("   plugins            - 查看插件列表")
        print("   visualize          - 生成可视化报告")
        print("   demo               - 运行系统演示")
        print("   quit               - 退出系统")
        print("="*50)
    
    def run_cli(self):
        """运行命令行界面"""
        print("🚀 启动多模型智能 Agent 系统...")
        self.show_status()
        
        while self.running:
            try:
                command = input("\n请输入命令: ").strip()
                
                if not command:
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    print("👋 正在关闭系统...")
                    self.running = False
                    self.scheduler.shutdown()
                    
                elif cmd == "status":
                    self.show_status()
                    
                elif cmd == "task" and len(parts) > 1:
                    task_input = " ".join(parts[1:])
                    result = self.process_task(task_input)
                    print(f"✅ 任务结果: {result}")
                    
                elif cmd == "optimize":
                    self.self_optimize()
                    print("✅ 自我优化完成")
                    
                elif cmd == "dialogue":
                    self.model_dialogue()
                    print("✅ 模型对话完成")
                    
                elif cmd == "test":
                    print("🔧 测试模型连接...")
                    test_results = self.model_manager.test_models()
                    
                    # 统计结果
                    total_models = len(test_results)
                    failed_models = sum(1 for status in test_results.values() if status == "失败")
                    success_models = total_models - failed_models
                    
                    for model, result in test_results.items():
                        status_emoji = "❌" if result == "失败" else "✅"
                        print(f"   {status_emoji} {model}: {result}")
                    
                    print("\n📊 测试结果统计:")
                    print(f"   总模型数: {total_models}")
                    print(f"   成功连接: {success_models}")
                    print(f"   连接失败: {failed_models}")
                    
                    if failed_models > 0:
                        print("\n💡 故障排除建议:")
                        print("   1. 检查 Ollama 服务是否正在运行")
                        print("   2. 确认模型是否已下载: ollama pull <model_name>")
                        print("   3. 检查网络连接是否正常")
                        print("   4. 查看 Ollama 日志了解详细信息")
                    
                    print("✅ 模型测试完成")
                    
                elif cmd == "history":
                    self.show_task_history()
                    
                elif cmd == "performance":
                    self.show_performance_report()
                    
                elif cmd == "config":
                    self.show_config()
                    
                elif cmd == "plugins":
                    self.show_plugins()
                    
                elif cmd == "visualize":
                    self.generate_visualization()
                    
                elif cmd == "demo":
                    self.run_demo()
                    
                else:
                    print("❌ 未知命令。请使用 'status' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n👋 收到中断信号，正在关闭系统...")
                self.running = False
                self.scheduler.shutdown()
                break
            except Exception as e:
                logging.error(f"命令执行错误: {e}")
                print(f"❌ 错误: {e}")

    def show_task_history(self):
        """显示任务历史"""
        try:
            history = self.task_history.get_recent_tasks(10)
            if history:
                print("\n📊 最近任务历史:")
                print("-" * 80)
                for task in history:
                    print(f"🆔 {task['id']} | 📝 {task['task_type']} | 🔧 {task['complexity']} | 🤖 {task['model_used']} | ⏰ {task['timestamp']}")
                print("-" * 80)
            else:
                print("📭 暂无任务历史记录")
        except Exception as e:
            print(f"❌ 获取任务历史失败: {e}")
    
    def show_performance_report(self):
        """显示性能报告"""
        try:
            report = self.performance_monitor.get_performance_report()
            print("\n📈 系统性能报告:")
            print("-" * 50)
            if 'error' in report:
                print(f"⚠️  {report['error']}")
            else:
                print(f"🖥️  CPU使用率: {report['averages']['cpu_percent']:.1f}%")
                print(f"💾 内存使用率: {report['averages']['memory_percent']:.1f}%")
                print(f"💿 磁盘使用率: {report['averages']['disk_percent']:.1f}%")
                print(f"📊 数据点数: {report['data_points']}")
                print(f"📈 趋势: {report['trend']}")
                print(f"🚨 告警数: {report['alerts_count']}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 获取性能报告失败: {e}")
    
    def show_config(self):
        """显示配置信息"""
        try:
            config = self.config_manager.get_config_summary()
            print("\n⚙️ 系统配置信息:")
            print("-" * 50)
            for key, value in config.items():
                print(f"🔧 {key}: {value}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 获取配置信息失败: {e}")
    
    def show_plugins(self):
        """显示插件列表"""
        try:
            plugins = self.plugin_manager.list_plugins()
            print("\n🔌 已加载插件:")
            print("-" * 50)
            if plugins:
                for plugin in plugins:
                    print(f"📦 {plugin}")
            else:
                print("📭 暂无已加载的插件")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 获取插件列表失败: {e}")
    
    def generate_visualization(self):
        """生成可视化报告"""
        try:
            print("📊 正在生成可视化报告...")
            # 获取性能数据
            perf_data = self.performance_monitor.get_metrics_history(60)
            if perf_data:
                self.data_visualizer.create_performance_dashboard(perf_data)
                print("✅ 可视化报告已生成，请查看 reports/ 目录")
            else:
                print("⚠️ 没有足够的性能数据生成可视化报告")
        except Exception as e:
            print(f"❌ 生成可视化报告失败: {e}")
    
    def run_demo(self):
        """运行系统演示"""
        print("\n🎭 启动系统演示...")
        
        demo_tasks = [
            "分析Python代码性能优化",
            "生成一个简单的Web应用框架",
            "优化数据库查询语句"
        ]
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"\n🎯 演示任务 {i}: {task}")
            result = self.process_task(task)
            print(f"✅ 结果: {result[:100]}..." if len(result) > 100 else f"✅ 结果: {result}")
            time.sleep(2)  # 短暂延迟
        
        print("\n🎉 演示完成！")
        print("📊 查看演示结果:")
        self.show_task_history()
        self.show_performance_report()

if __name__ == "__main__":
    try:
        agent = AgentSystem()
        agent.run_cli()
    except Exception as e:
        logging.error(f"系统启动失败: {e}")
        print(f"❌ 系统启动失败: {e}")
        sys.exit(1)
