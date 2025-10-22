#!/bin/bash

# CBG项目自动部署安装脚本
# 配置GitHub Webhook自动部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 配置变量
PROJECT_DIR="/usr/lingtong"
WEBHOOK_PORT="9000"
WEBHOOK_SECRET=$(openssl rand -hex 32)

echo "=========================================="
echo "  CBG项目自动部署安装脚本"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用root用户运行此脚本"
    exit 1
fi

# 1. 安装必要依赖
log_info "安装必要依赖..."

# 检测系统类型
if command -v yum &> /dev/null; then
    # CentOS/RHEL系统
    yum update -y
    yum install -y python3 python3-pip git curl firewalld
    systemctl start firewalld
    systemctl enable firewalld
elif command -v apt-get &> /dev/null; then
    # Ubuntu/Debian系统
    apt-get update
    apt-get install -y python3 python3-pip git curl ufw
else
    log_error "不支持的系统类型，请手动安装依赖"
    exit 1
fi

# 2. 安装Python依赖
log_info "安装Python依赖..."
pip3 install flask

# 3. 创建项目目录
log_info "创建项目目录..."
mkdir -p "$PROJECT_DIR"
mkdir -p "/var/log"

# 4. 设置脚本权限
log_info "设置脚本权限..."
chmod +x "$PROJECT_DIR/deploy/auto_deploy.sh"
chmod +x "$PROJECT_DIR/deploy/quick_deploy.sh"
chmod +x "$PROJECT_DIR/deploy/webhook_deploy.py"

# 5. 配置Webhook服务
log_info "配置Webhook服务..."
cp "$PROJECT_DIR/deploy/webhook-deploy.service" "/etc/systemd/system/"
systemctl daemon-reload
systemctl enable webhook-deploy

# 6. 创建环境配置文件
log_info "创建环境配置..."
cat > "$PROJECT_DIR/.env" << EOF
# GitHub Webhook配置
GITHUB_WEBHOOK_SECRET=$WEBHOOK_SECRET
REPO_NAME=your-username/MH
BRANCH=master

# 部署配置
PROJECT_DIR=$PROJECT_DIR
DEPLOY_SCRIPT=$PROJECT_DIR/deploy/auto_deploy.sh
LOG_FILE=/var/log/webhook_deploy.log
EOF

# 7. 配置防火墙（如果需要）
log_info "配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL防火墙
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=5000/tcp
    firewall-cmd --permanent --add-port=9000/tcp
    firewall-cmd --reload
elif command -v ufw &> /dev/null; then
    # Ubuntu/Debian防火墙
    ufw allow 80/tcp
    ufw allow 5000/tcp
    ufw allow 9000/tcp
fi

# 8. 启动服务
log_info "启动Webhook服务..."
systemctl start webhook-deploy
systemctl status webhook-deploy --no-pager

# 9. 显示配置信息
log_success "安装完成！"
echo ""
echo "=========================================="
echo "  配置信息"
echo "=========================================="
echo "项目目录: $PROJECT_DIR"
echo "Webhook端口: $WEBHOOK_PORT"
echo "Webhook密钥: $WEBHOOK_SECRET"
echo "应用地址: http://lingtong.xyz"
echo "API地址: http://lingtong.xyz/api/v1"
echo "Webhook URL: http://lingtong.xyz:9000/webhook"
echo "状态检查: http://lingtong.xyz:9000/status"
echo "=========================================="
echo ""

# 10. 显示GitHub Webhook配置说明
log_info "GitHub Webhook配置说明:"
echo ""
echo "1. 登录GitHub，进入您的仓库"
echo "2. 点击 Settings -> Webhooks -> Add webhook"
echo "3. 配置如下:"
echo "   - Payload URL: http://lingtong.xyz:9000/webhook"
echo "   - Content type: application/json"
echo "   - Secret: $WEBHOOK_SECRET"
echo "   - Events: 选择 'Just the push event'"
echo "   - Active: 勾选"
echo ""

# 11. 显示使用方法
log_info "使用方法:"
echo ""
echo "手动部署:"
echo "  $PROJECT_DIR/deploy/auto_deploy.sh deploy"
echo ""
echo "快速部署:"
echo "  $PROJECT_DIR/deploy/quick_deploy.sh"
echo ""
echo "查看状态:"
echo "  $PROJECT_DIR/deploy/auto_deploy.sh status"
echo ""
echo "查看日志:"
echo "  $PROJECT_DIR/deploy/auto_deploy.sh logs"
echo ""

log_success "自动部署系统安装完成！"
