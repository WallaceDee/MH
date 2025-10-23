#!/bin/bash

# CBG项目部署脚本 - 使用Nginx反向代理

echo "🚀 开始部署CBG项目..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查前端构建文件
echo "📁 检查前端构建文件..."
if [ ! -d "web/dist" ]; then
    echo "❌ 前端构建文件不存在，请先上传web/dist目录"
    exit 1
fi

if [ ! -f "web/dist/index.html" ]; then
    echo "❌ 前端构建文件不完整，缺少index.html"
    exit 1
fi

echo "✅ 前端构建文件检查通过"

# 停止现有容器
echo "🛑 停止现有容器..."
docker compose -f docker-compose.prod.yml down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker compose -f docker-compose.prod.yml up -d --build

# 检查服务状态
echo "🔍 检查服务状态..."
sleep 10

# 检查API服务健康状态
echo "🏥 检查API服务健康状态..."
API_HEALTH=$(curl -s http://localhost/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ API服务健康检查通过"
else
    echo "❌ API服务健康检查失败"
fi

# 检查前端访问
echo "🌐 检查前端访问..."
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [ "$FRONTEND_CHECK" = "200" ]; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常，HTTP状态码: $FRONTEND_CHECK"
fi

echo "🎉 部署完成！"
echo "📋 服务信息:"
echo "   - 前端访问: http://localhost/"
echo "   - 管理后台: http://localhost/admin.html"
echo "   - API健康检查: http://localhost/health"
echo "   - API接口: http://localhost/api/v1/"

# 显示容器状态
echo "📊 容器状态:"
docker compose -f docker-compose.prod.yml ps
