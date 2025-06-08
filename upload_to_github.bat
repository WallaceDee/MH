@echo off
echo 正在初始化 Git 仓库...
git config --global user.name "WallaceDee"
git config --global user.email "447363121@qq.com"
:: 初始化 Git 仓库
git init

:: 添加远程仓库
git remote add origin https://github.com/WallaceDee/MH.git

:: 添加所有文件到暂存区
git add .

:: 创建首次提交
git commit -m "Initial commit"

:: 设置主分支名称为 main
git branch -M main

:: 推送到远程仓库
git push -u origin main

echo.
echo 如果遇到认证问题，请确保：
echo 1. 已经登录 GitHub
echo 2. 已经配置了 Git 用户名和邮箱
echo    git config --global user.name "WallaceDee"
echo    git config --global user.email "447363121@qq.com"
echo.
pause 