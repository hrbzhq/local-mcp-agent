# 性能监控系统

## 概述

本系统提供全面的性能监控功能，包括实时系统指标收集、告警系统、性能报告生成和Web界面展示。

## 功能特性

### 🚀 核心功能

1. **按需性能监控**
   - 默认不启动自动监控，节省系统资源
   - 用户手动启动/停止监控
   - 智能检测### 📊 监控参数

- **history_size**: 历史数据存储大小（默认1000）
- **interval**: 监控间隔时间（秒，默认1.0）
- **update_interval**: Web界面更新间隔（默认5秒）
- **inactivity_timeout**: 用户无活动超时时间（默认5分钟）

## 资源优化特性

### 🔋 智能资源管理

1. **按需启动**
   - 系统启动时不自动开启性能监控
   - 只有用户主动点击"启动监控"按钮时才开始收集数据
   - 避免不必要的系统资源消耗

2. **自动停止机制**
   - **页面不可见检测**: 当用户切换到其他标签页或最小化窗口时，自动暂停监控
   - **用户活动检测**: 检测鼠标、键盘等用户活动，5分钟无活动自动停止监控
   - **页面卸载**: 用户关闭页面时自动停止监控并清理资源

3. **优化更新频率**
   - Web界面更新间隔从3秒调整为5秒，减少网络请求
   - 后端监控间隔保持1秒，但只有在用户主动监控时才运行
   - 图表数据点限制为20个，避免内存过度使用

4. **资源清理**
   - 定时器自动清理，防止内存泄漏
   - 图表实例在停止监控时正确销毁
   - 网络请求在组件卸载时取消

### 💡 使用建议

- **主动管理**: 只有在需要监控系统性能时才启动监控
- **及时停止**: 查看完性能数据后及时点击"停止监控"按钮
- **合理频率**: 5秒的更新频率在大多数场景下已足够实时
- **关注告警**: 主要通过告警系统获取重要性能信息，无需持续监控动停止监控
   - 页面不可见时自动暂停监控

2. **实时性能监控**
   - CPU使用率监控
   - 内存使用率监控
   - 磁盘使用率监控
   - 网络流量监控
   - 进程资源使用监控

3. **智能告警系统**
   - 可配置的性能阈值
   - 实时告警触发
   - 告警历史记录
   - 自定义告警回调

4. **性能报告生成**
   - 多时间段性能统计
   - 平均值和峰值分析
   - 趋势分析
   - 健康评分计算

5. **Web界面展示**
   - 实时性能仪表板
   - 交互式图表展示
   - 历史数据趋势图
   - 告警信息展示

## 技术架构

### 核心组件

- **PerformanceMonitor类**: 主要的性能监控引擎
- **Web API接口**: Flask REST API提供数据访问
- **前端界面**: Bootstrap + Chart.js构建的响应式界面
- **数据存储**: 内存队列存储历史数据

### 系统指标

| 指标类型 | 描述 | 单位 |
|---------|------|------|
| CPU使用率 | 系统CPU占用率 | % |
| 内存使用率 | 系统内存占用率 | % |
| 磁盘使用率 | 磁盘空间占用率 | % |
| 网络流量 | 发送/接收字节数 | MB |
| 进程内存 | 当前进程内存使用 | MB |
| 进程CPU | 当前进程CPU使用 | % |

## 使用方法

### 1. 启动性能监控

```python
from src.performance_monitor import PerformanceMonitor

# 创建监控实例
monitor = PerformanceMonitor()

# 启动监控（每2秒收集一次数据）
monitor.start_monitoring(interval=2.0)
```

### 2. 查看当前性能

```python
# 获取当前指标
current_metrics = monitor.get_current_metrics()

# 获取健康评分
health_score = monitor.get_system_health_score()
```

### 3. 生成性能报告

```python
# 生成最近1小时的报告
report = monitor.get_performance_report(minutes=60)
print(f"平均CPU使用率: {report['averages']['cpu_percent']:.1f}%")
```

### 4. 配置告警阈值

```python
# 设置CPU告警阈值
monitor.set_threshold('cpu_percent', 80.0)

# 添加告警回调
def alert_handler(alert):
    print(f"告警: {alert['message']}")

monitor.add_alert_callback(alert_handler)
```

## Web界面使用

### 访问地址
```
http://localhost:5000
```

### 主要功能

1. **仪表板页面**
   - 系统健康评分展示
   - 实时性能指标卡片
   - 性能趋势图表

2. **性能监控页面**
   - 详细的系统资源信息
   - 实时更新的图表
   - 告警历史记录
   - 性能报告生成

### API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/performance` | GET | 获取当前性能数据 |
| `/api/performance/history` | GET | 获取历史性能数据 |
| `/api/performance/report` | GET | 生成性能报告 |
| `/api/performance/start` | POST | 启动性能监控 |
| `/api/performance/stop` | POST | 停止性能监控 |

## 演示脚本

系统提供完整的演示脚本：

```bash
# 运行性能监控演示
python demonstrate_performance_monitoring.py

# 生成性能仪表板图表
python generate_performance_dashboard.py
```

## 配置说明

### 默认阈值设置

```python
thresholds = {
    'cpu_percent': 80.0,      # CPU使用率阈值
    'memory_percent': 85.0,   # 内存使用率阈值
    'disk_usage_percent': 90.0,  # 磁盘使用率阈值
    'response_time': 5.0,     # 响应时间阈值（秒）
    'error_rate': 0.1         # 错误率阈值
}
```

### 监控参数

- **history_size**: 历史数据存储大小（默认1000）
- **interval**: 监控间隔时间（秒，默认1.0）

## 健康评分算法

系统健康评分基于以下公式计算：

```
健康评分 = 100 - max(CPU使用率, 内存使用率, 磁盘使用率)
```

评分范围：0-100
- 80-100: 🟢 健康
- 60-79: 🟡 一般
- 0-59: 🔴 不良

## 日志和调试

### 日志文件
- `logs/performance_demo.log`: 演示脚本日志
- Flask应用日志输出到控制台

### 调试模式
Web应用默认启用调试模式，修改`web_app.py`中的`debug=True`可关闭。

## 扩展功能

### 自定义指标
可以通过继承`PerformanceMonitor`类添加自定义性能指标：

```python
class CustomPerformanceMonitor(PerformanceMonitor):
    def collect_custom_metrics(self):
        # 添加自定义指标收集逻辑
        pass
```

### 告警通知
支持多种告警通知方式：
- 控制台输出
- 日志记录
- 邮件通知（可扩展）
- Webhook通知（可扩展）

## 性能优化

### 内存管理
- 使用`deque`限制历史数据大小
- 定期清理过期告警记录

### CPU优化
- 异步监控线程
- 可配置的监控间隔
- 轻量级指标收集

## 故障排除

### 常见问题

1. **监控数据为空**
   - 检查psutil是否正确安装
   - 确认系统权限

2. **Web界面无法访问**
   - 检查端口5000是否被占用
   - 确认防火墙设置

3. **图表不显示**
   - 检查Chart.js库是否正确加载
   - 查看浏览器控制台错误

### 依赖包

```
psutil>=5.8.0
flask>=2.0.0
flask-cors>=3.0.0
flask-socketio>=5.0.0
matplotlib>=3.5.0
```

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2025-09-09
- **作者**: AI Assistant

## 许可证

本项目采用MIT许可证。</content>
<parameter name="filePath">d:\tools\allmcp\workagent\PERFORMANCE_MONITORING_README.md
