# 自主优化系统 (Autonomous Optimization System)

一个完整的AI自主优化框架，能够实现AI系统的自我改进、学习和进化。

## 系统架构

### 核心组件

#### 1. 自主优化核心 (Self-Optimization Core)
- **位置**: `src/self_optimization_core.py`
- **功能**: 系统的中枢，负责整体优化循环和系统状态评估
- **特性**:
  - 持续监控系统性能
  - 自动执行优化计划
  - 数据库驱动的优化历史记录

#### 2. 学习引擎 (Learning Engine)
- **位置**: `src/learning_engine.py`
- **功能**: 记录经验并识别学习模式
- **特性**:
  - 经验记录和存储
  - 模式识别和预测
  - 技能熟练度跟踪

#### 3. 决策制定器 (Decision Maker)
- **位置**: `src/decision_maker.py`
- **功能**: 基于历史数据和当前上下文做出智能决策
- **特性**:
  - 选项评估和排序
  - 置信度评分
  - 决策历史跟踪

#### 4. 资源管理器 (Resource Manager)
- **位置**: `src/resource_manager.py`
- **功能**: 监控和优化系统资源使用
- **特性**:
  - CPU/内存监控
  - 自动资源优化
  - 警报系统

#### 5. 安全监控器 (Safety Monitor)
- **位置**: `src/safety_monitor.py`
- **功能**: 确保系统安全通过规则基础监控
- **特性**:
  - 安全规则定义
  - 违规检测和处理
  - 紧急响应机制

#### 6. MCP自主优化器 (MCP Autonomous Optimizer)
- **位置**: `src/mcp_autonomous_optimizer.py`
- **功能**: 自主生成和优化MCP模块
- **特性**:
  - 需求扫描和分析
  - 自动代码生成
  - 性能优化

#### 7. 参谋中心 (Command Center)
- **位置**: `src/command_center.py`
- **功能**: 多模型协调与智能决策
- **特性**:
  - 任务智能分配
  - 模型性能监控
  - 系统协调管理

#### 8. 系统集成器 (System Integrator)
- **位置**: `src/system_integrator.py`
- **功能**: 整合所有自主优化组件
- **特性**:
  - 组件依赖管理
  - 系统初始化和关闭
  - 健康监控

## 安装和设置

### 环境要求
- Python 3.8+
- SQLite 3
- psutil (用于资源监控)

### 安装依赖
```bash
pip install psutil
```

### 运行系统

#### 交互模式 (推荐)
```bash
python autonomous_system_launcher.py --mode interactive
```

#### 自动模式
```bash
python autonomous_system_launcher.py --mode auto
```

## 使用方法

### 基本操作

启动系统后，您可以：

1. **查看系统状态**:
   ```
   自主优化系统 > status
   ```

2. **提交任务**:
   ```
   自主优化系统 > task 分析这个项目的代码结构
   ```

3. **查看性能报告**:
   ```
   自主优化系统 > performance
   ```

4. **管理组件**:
   ```
   自主优化系统 > enable learning_engine
   自主优化系统 > disable safety_monitor
   ```

### 高级功能

#### 自定义配置
编辑 `config/system_integration.json` 来：
- 启用/禁用组件
- 调整优化参数
- 配置模型设置

#### 扩展系统
要添加新的组件：
1. 在 `src/` 目录下创建组件文件
2. 在配置文件中注册组件
3. 实现必要的接口方法

## 系统特性

### 自主学习
- 系统能够从经验中学习
- 自动识别模式和趋势
- 基于历史数据做出预测

### 智能决策
- 多选项评估和排序
- 置信度计算
- 决策质量跟踪

### 资源优化
- 实时资源监控
- 自动优化建议
- 负载均衡

### 安全保障
- 规则基础的安全监控
- 违规自动检测
- 紧急响应机制

### 多模型协调
- 智能任务分配
- 模型性能评估
- 动态负载均衡

## 数据库结构

系统使用多个SQLite数据库：

- `optimization_history.db`: 优化历史记录
- `learning_data.db`: 学习数据和经验
- `decision_history.db`: 决策历史
- `safety_events.db`: 安全事件记录
- `command_center.db`: 参谋中心数据

## 日志系统

日志文件存储在 `logs/` 目录下：
- 自动按日期轮转
- 支持不同日志级别
- 包含详细的系统运行信息

## 故障排除

### 常见问题

1. **组件加载失败**
   - 检查组件文件是否存在
   - 验证依赖关系
   - 查看日志文件获取详细错误信息

2. **性能问题**
   - 检查资源使用情况
   - 调整优化参数
   - 启用/禁用特定组件

3. **安全警报**
   - 查看安全日志
   - 检查安全规则配置
   - 验证系统配置

### 调试模式
```bash
python autonomous_system_launcher.py --log-level DEBUG
```

## 扩展开发

### 添加新组件
1. 创建组件类，实现必要的接口
2. 在配置文件中注册组件
3. 添加组件依赖关系
4. 实现健康检查方法

### 自定义优化策略
1. 扩展学习引擎
2. 修改决策制定逻辑
3. 添加新的优化算法

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交问题和改进建议！

## 版本历史

- v1.0.0: 初始版本，包含所有核心组件
  - 自主优化核心
  - 学习引擎
  - 决策制定器
  - 资源管理器
  - 安全监控器
  - MCP优化器
  - 参谋中心
  - 系统集成器
