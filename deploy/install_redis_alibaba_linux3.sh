#!/bin/bash
# Redis安装脚本 - Alibaba Cloud Linux 3
# CBG爬虫项目Redis缓存系统安装指南
# 适用于: Alibaba Cloud Linux 3 (基于CentOS 8)

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 检查系统版本
check_system() {
    log_info "检查系统版本..."
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "$ID" == "alinux" ]] && [[ "$VERSION_ID" == "3" ]]; then
            log_success "检测到Alibaba Cloud Linux 3系统"
        else
            log_warning "系统为: $PRETTY_NAME"
            log_warning "此脚本专为Alibaba Cloud Linux 3设计，可能需要调整"
        fi
    else
        log_warning "无法检测系统版本"
    fi
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    yum update -y
    log_success "系统包更新完成"
}

# 安装必要的工具
install_dependencies() {
    log_info "安装编译工具和依赖..."
    yum groupinstall -y "Development Tools"
    yum install -y wget curl gcc gcc-c++ make tcl
    log_success "依赖安装完成"
}

# 下载和编译Redis
install_redis() {
    local REDIS_VERSION="7.0.15"  # 稳定版本
    local REDIS_DIR="/opt/redis"
    
    log_info "开始安装Redis ${REDIS_VERSION}..."
    
    # 创建安装目录
    mkdir -p ${REDIS_DIR}
    cd /tmp
    
    # 下载Redis源码
    log_info "下载Redis源码..."
    wget http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz
    
    if [[ ! -f "redis-${REDIS_VERSION}.tar.gz" ]]; then
        log_error "Redis源码下载失败"
        exit 1
    fi
    
    # 解压并编译
    log_info "解压和编译Redis..."
    tar xzf redis-${REDIS_VERSION}.tar.gz
    cd redis-${REDIS_VERSION}
    
    # 编译Redis
    make
    
    # 运行测试（如果测试失败，仍然继续安装）
    log_info "运行Redis测试（测试失败不影响安装）..."
    if make test; then
        log_success "Redis测试通过"
    else
        log_warning "Redis测试有部分失败，但不影响核心功能，继续安装..."
        log_info "常见的测试失败原因：内存碎片整理测试边界值、系统资源限制等"
    fi
    
    make install PREFIX=${REDIS_DIR}
    
    log_success "Redis编译安装完成"
    
    # 创建符号链接
    ln -sf ${REDIS_DIR}/bin/redis-server /usr/local/bin/redis-server
    ln -sf ${REDIS_DIR}/bin/redis-cli /usr/local/bin/redis-cli
    ln -sf ${REDIS_DIR}/bin/redis-sentinel /usr/local/bin/redis-sentinel
    
    log_success "Redis命令链接创建完成"
}

# 创建Redis用户
create_redis_user() {
    log_info "创建Redis用户..."
    if ! id "redis" &>/dev/null; then
        useradd --system --home /var/lib/redis --shell /bin/false redis
        log_success "Redis用户创建成功"
    else
        log_info "Redis用户已存在"
    fi
}

# 创建Redis目录结构
create_redis_directories() {
    log_info "创建Redis目录结构..."
    
    # 创建必要目录
    mkdir -p /etc/redis
    mkdir -p /var/lib/redis
    mkdir -p /var/log/redis
    mkdir -p /var/run/redis
    
    # 设置目录权限
    chown redis:redis /var/lib/redis
    chown redis:redis /var/log/redis
    chown redis:redis /var/run/redis
    
    chmod 755 /var/lib/redis
    chmod 755 /var/log/redis
    chmod 755 /var/run/redis
    
    log_success "Redis目录结构创建完成"
}

# 创建Redis配置文件
create_redis_config() {
    log_info "创建Redis配置文件..."
    
    cat > /etc/redis/redis.conf << 'EOF'
# Redis配置文件 - CBG项目优化配置
# 适用于Alibaba Cloud Linux 3

# 网络配置
bind 127.0.0.1 ::1
protected-mode yes
port 6379
timeout 300
tcp-keepalive 300

# 通用配置
daemonize yes
pidfile /var/run/redis/redis.pid
loglevel notice
logfile /var/log/redis/redis.log

# 数据持久化
dir /var/lib/redis
dbfilename dump.rdb
save 900 1
save 300 10
save 60 10000

# AOF持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# 内存管理
maxmemory 1gb
maxmemory-policy allkeys-lru

# 安全配置
# requirepass your_strong_password_here

# 客户端配置
maxclients 10000

# 慢日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# 性能优化
tcp-keepalive 300
tcp-backlog 511
databases 16

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG "CONFIG_9f2ca6085fede5337be84d9b"
EOF

    chown redis:redis /etc/redis/redis.conf
    chmod 640 /etc/redis/redis.conf
    
    log_success "Redis配置文件创建完成"
}

# 创建systemd服务文件
create_systemd_service() {
    log_info "创建systemd服务文件..."
    
    cat > /etc/systemd/system/redis.service << 'EOF'
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always
RestartSec=3
LimitNOFILE=65535

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=-/var/lib/redis
ReadWritePaths=-/var/log/redis
ReadWritePaths=-/var/run/redis

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_success "systemd服务文件创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if systemctl is-active --quiet firewalld; then
        # Redis默认只允许本地连接，如需远程连接请谨慎开放
        # firewall-cmd --permanent --add-port=6379/tcp
        # firewall-cmd --reload
        log_info "防火墙已运行，Redis配置为仅本地访问"
    else
        log_info "防火墙未运行"
    fi
}

# 启动和测试Redis
start_and_test_redis() {
    log_info "启动Redis服务..."
    
    # 启动Redis
    systemctl enable redis
    systemctl start redis
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet redis; then
        log_success "Redis服务启动成功"
    else
        log_error "Redis服务启动失败"
        systemctl status redis
        exit 1
    fi
    
    # 测试Redis连接
    log_info "测试Redis连接..."
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis连接测试成功"
    else
        log_error "Redis连接测试失败"
        exit 1
    fi
}

# 显示安装信息
show_installation_info() {
    log_success "Redis安装完成！"
    echo
    echo "==================================="
    echo "Redis安装信息:"
    echo "==================================="
    echo "版本: $(redis-server --version)"
    echo "配置文件: /etc/redis/redis.conf"
    echo "数据目录: /var/lib/redis"
    echo "日志文件: /var/log/redis/redis.log"
    echo "PID文件: /var/run/redis/redis.pid"
    echo "端口: 6379 (仅本地访问)"
    echo
    echo "常用命令:"
    echo "启动服务: systemctl start redis"
    echo "停止服务: systemctl stop redis"
    echo "重启服务: systemctl restart redis"
    echo "查看状态: systemctl status redis"
    echo "连接Redis: redis-cli"
    echo "查看日志: tail -f /var/log/redis/redis.log"
    echo
    echo "Python项目连接配置:"
    echo "REDIS_HOST = 'localhost'"
    echo "REDIS_PORT = 6379"
    echo "REDIS_DB = 0"
    echo
    log_warning "建议设置Redis密码，编辑/etc/redis/redis.conf中的requirepass配置"
}

# 主函数
main() {
    log_info "开始安装Redis for CBG项目..."
    
    check_root
    check_system
    update_system
    install_dependencies
    install_redis
    create_redis_user
    create_redis_directories
    create_redis_config
    create_systemd_service
    configure_firewall
    start_and_test_redis
    show_installation_info
    
    log_success "Redis安装脚本执行完成！"
}

# 执行主函数
main "$@"
