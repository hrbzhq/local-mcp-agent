# Git 安装和项目发布脚本

Write-Host "🚀 Local MCP Agent - GitHub 发布助手" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 检查 Git 是否已安装
$gitInstalled = $false
try {
    $gitVersion = git --version
    Write-Host "✅ Git 已安装: $gitVersion" -ForegroundColor Green
    $gitInstalled = $true
}
catch {
    Write-Host "❌ 未检测到 Git，正在安装..." -ForegroundColor Yellow
}

# 如果 Git 未安装，使用 winget 安装
if (-not $gitInstalled) {
    try {
        Write-Host "📦 使用 winget 安装 Git..." -ForegroundColor Blue
        winget install --id Git.Git -e --source winget
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Git 安装完成！请重新运行此脚本。" -ForegroundColor Green
        Write-Host "💡 如果命令仍不可用，请重启终端或计算机。" -ForegroundColor Yellow
        exit 0
    }
    catch {
        Write-Host "❌ 自动安装失败。请手动安装 Git:" -ForegroundColor Red
        Write-Host "   1. 访问 https://git-scm.com/download/win" -ForegroundColor Yellow
        Write-Host "   2. 下载并安装 Git for Windows" -ForegroundColor Yellow
        Write-Host "   3. 重启终端后重新运行此脚本" -ForegroundColor Yellow
        exit 1
    }
}

# Git 已安装，继续项目发布流程
Write-Host ""
Write-Host "🔧 开始项目发布流程..." -ForegroundColor Blue

# 检查是否在正确目录
if (-not (Test-Path "README.md") -or -not (Test-Path "LICENSE")) {
    Write-Host "❌ 错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 项目目录验证通过" -ForegroundColor Green

# 初始化 Git 仓库
Write-Host ""
Write-Host "📁 初始化 Git 仓库..." -ForegroundColor Blue

if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git 仓库初始化完成" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Git 仓库已存在" -ForegroundColor Yellow
}

# 配置 Git 用户信息（如果尚未配置）
$gitUser = git config --global user.name
$gitEmail = git config --global user.email

if (-not $gitUser) {
    $userName = Read-Host "请输入您的 Git 用户名"
    git config --global user.name "$userName"
}

if (-not $gitEmail) {
    $userEmail = Read-Host "请输入您的 Git 邮箱"
    git config --global user.email "$userEmail"
}

Write-Host "✅ Git 用户配置完成" -ForegroundColor Green

# 添加所有文件
Write-Host ""
Write-Host "📝 添加项目文件..." -ForegroundColor Blue
git add .

# 提交初始版本
Write-Host "💾 创建初始提交..." -ForegroundColor Blue
git commit -m "feat: Initial commit - Local MCP Agent v2.0.0

🚀 Complete local AI agent solution with:
- MCP (Model Context Protocol) server implementation
- FastAPI backend with 7 core endpoints
- VS Code extension with TypeScript
- Multi-model support (Ollama ecosystem)
- Performance optimizations (3 core tools)
- Docker containerization
- Complete documentation system
- CI/CD automation with GitHub Actions

✨ Features:
- Intelligent model routing and auto-selection
- Multi-model collaborative chat
- RESTful API design
- Production-ready architecture
- Enterprise-grade documentation
- Open source with MIT license

🎯 Ready for community contribution and production deployment!"

Write-Host "✅ 初始提交完成" -ForegroundColor Green

# 创建主分支
Write-Host ""
Write-Host "🌿 设置主分支..." -ForegroundColor Blue
git branch -M main
Write-Host "✅ 主分支设置完成" -ForegroundColor Green

# 提示用户创建 GitHub 仓库
Write-Host ""
Write-Host "🌐 接下来需要创建 GitHub 仓库:" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "1. 访问 https://github.com/new" -ForegroundColor White
Write-Host "2. 仓库名称: local-mcp-agent" -ForegroundColor White
Write-Host "3. 描述: Complete local AI agent solution with MCP protocol, multi-model support, and VS Code integration" -ForegroundColor White
Write-Host "4. 设置为 Public（公开）" -ForegroundColor White
Write-Host "5. 不要勾选 'Add a README file'（我们已经有了）" -ForegroundColor White
Write-Host "6. 不要勾选 'Add .gitignore'（我们已经有了）" -ForegroundColor White
Write-Host "7. License 选择 'MIT License'（或跳过，我们已经有了）" -ForegroundColor White
Write-Host "8. 点击 'Create repository'" -ForegroundColor White

Write-Host ""
$repoUrl = Read-Host "请输入创建的仓库 URL (例如: https://github.com/yourusername/local-mcp-agent.git)"

if ($repoUrl) {
    Write-Host ""
    Write-Host "🔗 添加远程仓库..." -ForegroundColor Blue
    
    # 移除可能存在的 origin
    try {
        git remote remove origin 2>$null
    } catch {}
    
    # 添加新的远程仓库
    git remote add origin $repoUrl
    Write-Host "✅ 远程仓库添加完成" -ForegroundColor Green
    
    # 推送到 GitHub
    Write-Host ""
    Write-Host "⬆️  推送到 GitHub..." -ForegroundColor Blue
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 项目发布成功！" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "📁 仓库地址: $repoUrl" -ForegroundColor White
        Write-Host "🌟 请访问仓库页面完成以下操作:" -ForegroundColor Yellow
        Write-Host "   1. 检查项目文件是否完整上传" -ForegroundColor White
        Write-Host "   2. 编辑仓库描述和标签" -ForegroundColor White
        Write-Host "   3. 添加项目主题标签: ai, mcp, fastapi, vscode-extension, ollama" -ForegroundColor White
        Write-Host "   4. 创建第一个 Release (v2.0.0)" -ForegroundColor White
        Write-Host "   5. 设置 GitHub Pages（如果需要文档站点）" -ForegroundColor White
        
        Write-Host ""
        Write-Host "📦 下一步可以做的:" -ForegroundColor Yellow
        Write-Host "   - 发布到 VS Code Marketplace" -ForegroundColor White
        Write-Host "   - 提交到 Docker Hub" -ForegroundColor White
        Write-Host "   - 在社区分享（Reddit, Hacker News）" -ForegroundColor White
        Write-Host "   - 添加更多使用示例" -ForegroundColor White
        
    } else {
        Write-Host ""
        Write-Host "❌ 推送失败，请检查:" -ForegroundColor Red
        Write-Host "   1. 仓库 URL 是否正确" -ForegroundColor Yellow
        Write-Host "   2. 是否有推送权限" -ForegroundColor Yellow
        Write-Host "   3. 网络连接是否正常" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 您可以稍后手动推送:" -ForegroundColor Blue
        Write-Host "   git push -u origin main" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  跳过远程仓库设置" -ForegroundColor Yellow
    Write-Host "💡 您可以稍后手动添加:" -ForegroundColor Blue
    Write-Host "   git remote add origin [repository_url]" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "🎊 Local MCP Agent 项目准备完成！" -ForegroundColor Green
Write-Host "感谢您使用此发布助手。" -ForegroundColor Blue
