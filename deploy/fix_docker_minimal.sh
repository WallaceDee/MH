#!/bin/bash
# Docker服务轻量级修复脚本 - 适用于低内存服务器
# 专门针对内存不足的情况进行优化

set -e

# 颜色输出函数
print_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

print_step() {
    echo -e "\033[36m[STEP]\033[0m $1"
}

# 检查系统资源
check_resources() {
    print_step "检查系统资源..."
    
    # 获取内存信息
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    
    print_info "总内存: ${TOTAL_MEM}MB"
    print_info "可用内存: ${AVAILABLE_MEM}MB"
    
    if [ "$TOTAL_MEM" -lt 1024 ]; then
        print_warning "⚠️  系统内存较低 (${TOTAL_MEM}MB)，将使用轻量级配置"
        LOW_MEMORY=true
    else
        LOW_MEMORY=false
    fi
    
    # 检查磁盘空间
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 80 ]; then
        print_warning "⚠️  磁盘使用率较高: ${DISK_USAGE}%"
    fi
}

# 创建轻量级Docker配置
create_minimal_config() {
    print_step "创建轻量级Docker配置..."
    
    # 备份现有配置
    if [ -f /etc/docker/daemon.json ]; then
        cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%s)
        print_info "已备份现有配置"
    fi
    
    # 创建针对低内存优化的配置
    mkdir -p /etc/docker
    
    if [ "$LOW_MEMORY" = true ]; then
        cat > /etc/docker/daemon.json << 'EOF'
{
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "1"
    },
    "default-ulimits": {
        "nofile": {
            "Name": "nofile",
            "Hard": 1024,
            "Soft": 1024
        }
    },
    "max-concurrent-downloads": 1,
    "max-concurrent-uploads": 1
}
EOF
        print_info "已创建低内存优化配置"
    else
        cat > /etc/docker/daemon.json << 'EOF'
{
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "50m",
        "max-file": "2"
    }
}
EOF
        print_info "已创建标准配置"
    fi
}

# 清理Docker文件（温和方式）
gentle_cleanup() {
    print_step "温和清理Docker文件..."
    
    # 停止Docker服务（如果在运行）
    systemctl stop docker 2>/dev/null || true
    
    # 等待进程完全停止
    sleep 3
    
    # 温和清理socket文件
    [ -f /var/run/docker.sock ] && rm -f /var/run/docker.sock
    [ -f /var/run/docker.pid ] && rm -f /var/run/docker.pid
    
    print_info "清理完成"
}

# 检查内核模块
ensure_kernel_modules() {
    print_step "检查内核模块..."
    
    # 检查并加载overlay模块
    if ! lsmod | grep -q overlay; then
        print_info "加载overlay模块..."
        modprobe overlay || print_warning "overlay模块加载失败"
    fi
    
    # 检查并加载br_netfilter模块
    if ! lsmod | grep -q br_netfilter; then
        print_info "加载br_netfilter模块..."
        modprobe br_netfilter || print_warning "br_netfilter模块加载失败"
    fi
}

# 启动Docker服务
start_docker_service() {
    print_step "启动Docker服务..."
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    # 启动Docker服务
    print_info "正在启动Docker服务..."
    if systemctl start docker; then
        print_info "✅ Docker服务启动成功"
        
        # 等待服务完全启动
        sleep 5
        
        # 验证服务状态
        if systemctl is-active --quiet docker; then
            print_info "✅ Docker服务运行正常"
            
            # 设置开机自启
            systemctl enable docker
            print_info "✅ 已设置开机自启"
            
            return 0
        else
            print_error "❌ Docker服务启动后异常"
            return 1
        fi
    else
        print_error "❌ Docker服务启动失败"
        return 1
    fi
}

# 简单测试Docker
simple_test() {
    print_step "测试Docker基本功能..."
    
    # 测试docker info
    if timeout 30 docker info > /dev/null 2>&1; then
        print_info "✅ Docker info命令正常"
        return 0
    else
        print_warning "⚠️  Docker info命令超时或失败"
        return 1
    fi
}

# 显示服务状态
show_status() {
    print_step "Docker服务状态"
    
    echo "========================================="
    if systemctl is-active --quiet docker; then
        echo "✅ Docker服务状态: $(systemctl is-active docker)"
        echo "✅ Docker开机自启: $(systemctl is-enabled docker)"
        echo "✅ Docker版本: $(docker --version)"
        
        # 显示内存使用情况
        echo ""
        echo "当前系统资源:"
        free -h | head -2
        
        echo ""
        echo "下一步操作:"
        echo "1. 安装Docker Compose: ./deploy/install_docker_compose.sh"
        echo "2. 部署CBG项目: ./deploy/docker-deploy.sh --skip-build"
        
    else
        echo "❌ Docker服务未运行"
        echo ""
        echo "查看详细错误:"
        echo "sudo journalctl -u docker.service -n 10"
        echo ""
        echo "手动启动测试:"
        echo "sudo systemctl start docker"
    fi
    echo "========================================="
}

# 内存不足的特殊处理
handle_low_memory() {
    if [ "$LOW_MEMORY" = true ]; then
        print_warning "检测到低内存环境，建议:"
        echo "1. 考虑升级服务器内存到至少2GB"
        echo "2. 启用swap分区增加虚拟内存"
        echo "3. 使用轻量级容器镜像"
        echo "4. 限制同时运行的容器数量"
        echo ""
        
        # 询问是否创建swap
        read -p "是否创建1GB swap分区？(y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_swap
        fi
    fi
}

# 创建swap分区
create_swap() {
    print_step "创建swap分区..."
    
    # 检查是否已有swap
    if swapon -s | grep -q '/swapfile'; then
        print_info "swap分区已存在"
        return 0
    fi
    
    # 创建1GB swap文件
    dd if=/dev/zero of=/swapfile bs=1M count=1024 status=progress
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # 添加到fstab
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    
    print_info "✅ 1GB swap分区创建完成"
    free -h
}

# 主函数
main() {
    print_info "开始轻量级Docker服务修复..."
    
    # 检查root权限
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    check_resources
    handle_low_memory
    create_minimal_config
    gentle_cleanup
    ensure_kernel_modules
    
    if start_docker_service; then
        simple_test
        show_status
        print_info "✅ Docker服务修复完成！"
        return 0
    else
        print_error "❌ Docker服务修复失败"
        show_status
        return 1
    fi
}

# 执行主函数
main "$@"
