@echo off
title CBG爬虫一键启动
echo 🚀 CBG爬虫一键启动中...
echo.

REM 检查Node.js是否安装
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Node.js，正在为您安装...
    echo.
    winget install OpenJS.NodeJS.LTS
    if %errorlevel% neq 0 (
        echo ❌ Node.js安装失败！
        echo 请访问 https://nodejs.org 手动下载安装Node.js
        echo.
        pause
        exit /b 1
    )
    echo ✅ Node.js安装成功！
    echo.
    REM 刷新环境变量
    call refreshenv
)

REM 配置npm淘宝镜像
call npm config set registry https://registry.npmmirror.com

REM 检查web目录依赖
cd web
if not exist "node_modules" (
    echo 📦 首次运行，正在安装前端依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败！
        echo 请检查网络连接或手动运行 npm install
        echo.
        pause
        exit /b 1
    )
)
cd ..

echo ✅ 环境检查完成
echo.
echo 🌐 正在启动服务...
echo 📱 前端地址: http://localhost:8080
echo 🔗 后端地址: http://localhost:5000
echo.
echo ⚠️  请不要关闭此窗口，服务正在运行中...
echo 💡 按 Ctrl+C 可以停止所有服务
echo.

REM 在新窗口启动后端
start "CBG爬虫后端API" /min cmd /c "python start_backend.py"

REM 等待2秒让后端启动
timeout /t 2 /nobreak >nul

REM 在新窗口启动前端
start "CBG爬虫前端" cmd /c "cd web && call npm run serve"

REM 等待5秒后自动打开浏览器
timeout /t 5 /nobreak >nul
start http://localhost:8080

echo 🎉 启动完成！
echo.
echo 📋 使用说明：
echo    - 前端界面已在浏览器中打开
echo    - 后端API在后台运行
echo    - 关闭此窗口将停止所有服务
echo.

REM 保持主窗口开启
:loop
timeout /t 5 /nobreak >nul
goto loop 