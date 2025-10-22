#!/bin/bash

# 测试前端构建脚本

set -e

echo "🔍 检查前端构建环境..."

# 检查Node.js版本
echo "Node.js版本:"
node --version

# 检查npm版本
echo "npm版本:"
npm --version

# 进入web目录
cd web

# 检查package.json
echo "📦 检查package.json..."
if [ -f "package.json" ]; then
    echo "✅ package.json 存在"
    echo "构建脚本:"
    cat package.json | grep -A 10 '"scripts"'
else
    echo "❌ package.json 不存在"
    exit 1
fi

# 安装依赖
echo "📥 安装前端依赖..."
npm install --production=false

# 检查node_modules
echo "📁 检查node_modules..."
if [ -d "node_modules" ]; then
    echo "✅ node_modules 存在"
    echo "依赖数量: $(ls node_modules | wc -l)"
else
    echo "❌ node_modules 不存在"
    exit 1
fi

# 构建前端
echo "🔨 构建前端..."
npm run build

# 检查构建结果
echo "📁 检查构建结果..."
if [ -d "dist" ]; then
    echo "✅ dist 目录存在"
    echo "构建文件:"
    ls -la dist/
    echo "index.html 内容预览:"
    head -20 dist/index.html
else
    echo "❌ dist 目录不存在"
    exit 1
fi

echo "🎉 前端构建测试完成！"
