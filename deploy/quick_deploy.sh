#!/bin/bash

# CBG项目快速部署脚本
# 适用于开发环境的快速部署

set -e

# 配置
REPO_URL="git@github.com:WallaceDee/MH.git"
BRANCH="master"
PROJECT_DIR="/usr/lingtong"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 CBG项目快速部署${NC}"

# 检查并创建目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 创建项目目录..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# 拉取或更新代码
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    echo "📥 克隆代码..."
    git clone -b "$BRANCH" "$REPO_URL" .
fi

# 停止旧服务
echo "🛑 停止旧服务..."
docker-compose -f docker-compose.prod.yml down || true

# 构建并启动
echo "🔨 构建并启动服务..."
docker-compose -f docker-compose.prod.yml up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查状态
if docker ps | grep -q "cbg-spider-app"; then
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo "🌐 访问地址: http://localhost"
    echo "🔧 API地址: http://localhost/api/v1"
else
    echo "❌ 部署失败，请检查日志"
    docker-compose -f docker-compose.prod.yml logs
fi
