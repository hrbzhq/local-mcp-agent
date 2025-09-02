# Local MCP Agent - GitHub Publishing Script
# Author: AI Assistant
# Date: 2025-09-02

Write-Host "Local MCP Agent - GitHub Publishing Assistant" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Step 1: Check Git installation
Write-Host ""
Write-Host "Step 1: Checking Git installation..." -ForegroundColor Blue

try {
    $gitVersion = git --version
    Write-Host "Git is installed: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "Git is not installed. Installing via winget..." -ForegroundColor Yellow
    try {
        winget install --id Git.Git -e --source winget
        Write-Host "Git installed successfully! Please restart terminal and run this script again." -ForegroundColor Green
        exit 0
    }
    catch {
        Write-Host "Failed to install Git automatically. Please install manually:" -ForegroundColor Red
        Write-Host "1. Visit https://git-scm.com/download/win" -ForegroundColor Yellow
        Write-Host "2. Download and install Git for Windows" -ForegroundColor Yellow
        Write-Host "3. Restart terminal and run this script again" -ForegroundColor Yellow
        exit 1
    }
}

# Step 2: Verify project directory
Write-Host ""
Write-Host "Step 2: Verifying project directory..." -ForegroundColor Blue

if (-not (Test-Path "README.md") -or -not (Test-Path "LICENSE")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}
Write-Host "Project directory verified successfully" -ForegroundColor Green

# Step 3: Initialize Git repository
Write-Host ""
Write-Host "Step 3: Initializing Git repository..." -ForegroundColor Blue

if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "Git repository already exists" -ForegroundColor Yellow
}

# Step 4: Configure Git user (if needed)
Write-Host ""
Write-Host "Step 4: Configuring Git user..." -ForegroundColor Blue

$gitUser = git config --global user.name
$gitEmail = git config --global user.email

if (-not $gitUser) {
    $userName = Read-Host "Enter your Git username"
    git config --global user.name "$userName"
}

if (-not $gitEmail) {
    $userEmail = Read-Host "Enter your Git email"
    git config --global user.email "$userEmail"
}

Write-Host "Git user configuration completed" -ForegroundColor Green

# Step 5: Add and commit files
Write-Host ""
Write-Host "Step 5: Adding and committing files..." -ForegroundColor Blue

git add .
git commit -m "feat: Initial commit - Local MCP Agent v2.0.0

Complete local AI agent solution featuring:
- MCP protocol server with 3 optimized tools
- FastAPI backend with 7 core endpoints  
- VS Code extension with TypeScript
- Multi-model support via Ollama
- Performance optimizations and monitoring
- Docker containerization support
- Complete documentation system
- CI/CD automation with GitHub Actions

Ready for production deployment and community contribution."

Write-Host "Initial commit completed" -ForegroundColor Green

# Step 6: Set main branch
Write-Host ""
Write-Host "Step 6: Setting main branch..." -ForegroundColor Blue
git branch -M main
Write-Host "Main branch configured" -ForegroundColor Green

# Step 7: Instructions for GitHub repository creation
Write-Host ""
Write-Host "Step 7: GitHub Repository Creation" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow
Write-Host "Please follow these steps to create your GitHub repository:" -ForegroundColor White
Write-Host ""
Write-Host "1. Visit https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: local-mcp-agent" -ForegroundColor Cyan
Write-Host "3. Description: Complete local AI agent with MCP protocol and multi-model support" -ForegroundColor Cyan
Write-Host "4. Set as Public repository" -ForegroundColor Cyan
Write-Host "5. DO NOT add README, .gitignore, or license (we already have them)" -ForegroundColor Cyan
Write-Host "6. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""

$proceed = Read-Host "Have you created the repository? (y/n)"

if ($proceed -eq "y" -or $proceed -eq "Y") {
    $repoUrl = Read-Host "Enter the repository URL (e.g., https://github.com/username/local-mcp-agent.git)"
    
    if ($repoUrl) {
        Write-Host ""
        Write-Host "Step 8: Adding remote repository..." -ForegroundColor Blue
        
        # Remove existing origin if any
        try { git remote remove origin 2>$null } catch {}
        
        # Add new remote
        git remote add origin $repoUrl
        Write-Host "Remote repository added" -ForegroundColor Green
        
        # Push to GitHub
        Write-Host ""
        Write-Host "Step 9: Pushing to GitHub..." -ForegroundColor Blue
        git push -u origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "SUCCESS! Project published to GitHub!" -ForegroundColor Green
            Write-Host "=======================================" -ForegroundColor Green
            Write-Host "Repository URL: $repoUrl" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "1. Visit your repository and verify all files are uploaded" -ForegroundColor White
            Write-Host "2. Add repository topics: ai, mcp, fastapi, vscode-extension, ollama" -ForegroundColor White
            Write-Host "3. Create your first release (v2.0.0)" -ForegroundColor White
            Write-Host "4. Share with the community!" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "Push failed. Please check:" -ForegroundColor Red
            Write-Host "1. Repository URL is correct" -ForegroundColor Yellow
            Write-Host "2. You have push permissions" -ForegroundColor Yellow
            Write-Host "3. Network connection is stable" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "No problem! You can complete the process later with:" -ForegroundColor Blue
    Write-Host "git remote add origin [your-repo-url]" -ForegroundColor White
    Write-Host "git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "Local MCP Agent publishing assistant completed!" -ForegroundColor Green
