#!/bin/bash

# 开始部署
echo "=== Starting Deployment ==="

# 设置错误处理
set -e  # 如果有任何命令失败，脚本将立即退出

# 输出当前时间
echo "Deployment started at: $(date)"

# 进入项目目录（如果需要）
# cd /path/to/your/project

# 安装依赖（如果有必要）
echo "Installing dependencies..."
npm install

# 清理项目
echo "Cleaning the project..."
npm run clean

# 构建项目（如果有构建步骤）
echo "Building the project..."
npm run build  # 根据你的项目构建命令进行调整

# 执行部署命令
echo "Deploying the application..."

npm run deploy

# 输出部署完成的时间
echo "Deployment completed at: $(date)"

# 结束部署
echo "=== Deployment Finished ==="