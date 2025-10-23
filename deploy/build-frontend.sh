#!/bin/bash

# CBG前端构建脚本

echo "🚀 开始构建CBG前端项目..."

# 进入前端目录
cd web

# 检查是否存在node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 构建前端项目
echo "🔨 构建前端项目..."
npm run build

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "✅ 前端构建成功！"
    echo "📁 构建文件位置: web/dist/"
    
    # 显示构建文件大小
    echo "📊 构建文件信息:"
    du -sh dist/
    ls -la dist/
else
    echo "❌ 前端构建失败！"
    exit 1
fi

echo "🎉 前端构建完成！"
