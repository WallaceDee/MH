#!/bin/bash

# 私有仓库部署设置脚本
# 配置SSH密钥和克隆私有仓库

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  私有仓库部署设置"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用root用户运行此脚本"
    exit 1
fi

# 1. 安装必要工具
log_info "安装必要工具..."
apt-get update
apt-get install -y git openssh-client

# 2. 创建项目目录
log_info "创建项目目录..."
mkdir -p /usr/lingtong
chown $SUDO_USER:$SUDO_USER /usr/lingtong

# 3. 检查SSH密钥
log_info "检查SSH密钥..."
if [ ! -f "/home/$SUDO_USER/.ssh/id_rsa" ]; then
    log_warning "未找到SSH密钥，正在生成..."
    
    # 生成SSH密钥
    sudo -u $SUDO_USER ssh-keygen -t rsa -b 4096 -C "$SUDO_USER@$(hostname)" -f "/home/$SUDO_USER/.ssh/id_rsa" -N ""
    
    log_success "SSH密钥已生成"
    echo ""
    echo "请将以下公钥添加到GitHub:"
    echo "=========================================="
    cat /home/$SUDO_USER/.ssh/id_rsa.pub
    echo "=========================================="
    echo ""
    echo "添加步骤："
    echo "1. 复制上面的公钥内容"
    echo "2. 登录GitHub -> Settings -> SSH and GPG keys"
    echo "3. 点击 'New SSH key'"
    echo "4. 粘贴公钥并保存"
    echo ""
    read -p "添加完成后按回车继续..."
else
    log_success "SSH密钥已存在"
fi

# 4. 测试SSH连接
log_info "测试GitHub SSH连接..."
if sudo -u $SUDO_USER ssh -o StrictHostKeyChecking=no -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    log_success "GitHub SSH连接正常"
else
    log_warning "GitHub SSH连接失败，请检查SSH密钥配置"
    echo "手动测试命令："
    echo "sudo -u $SUDO_USER ssh -T git@github.com"
fi

# 5. 克隆私有仓库
log_info "克隆私有仓库..."
cd /usr/lingtong

if [ -d ".git" ]; then
    log_warning "项目目录已存在，跳过克隆"
else
    sudo -u $SUDO_USER git clone git@github.com:WallaceDee/MH.git .
    log_success "私有仓库克隆完成"
fi

# 6. 设置权限
log_info "设置文件权限..."
chown -R $SUDO_USER:$SUDO_USER /usr/lingtong
chmod +x /usr/lingtong/deploy/*.sh
chmod +x /usr/lingtong/deploy/webhook_deploy.py

# 7. 安装自动部署系统
log_info "安装自动部署系统..."
cd /usr/lingtong
sudo -u $SUDO_USER bash deploy/setup_auto_deploy.sh

log_success "私有仓库部署设置完成！"
echo ""
echo "=========================================="
echo "  部署信息"
echo "=========================================="
echo "项目目录: /usr/lingtong"
echo "应用地址: http://lingtong.xyz"
echo "API地址: http://lingtong.xyz/api/v1"
echo "Webhook: http://lingtong.xyz:9000/webhook"
echo "=========================================="
echo ""
echo "后续使用："
echo "1. 推送代码到GitHub会自动部署"
echo "2. 手动部署: /usr/lingtong/deploy/auto_deploy.sh deploy"
echo "3. 查看状态: /usr/lingtong/deploy/auto_deploy.sh status"
