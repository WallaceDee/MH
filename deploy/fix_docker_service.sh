#!/bin/bash
# Docker服务问题诊断和修复脚本
# 解决Docker服务启动失败的问题

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

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
}

# 诊断Docker服务状态
diagnose_docker_service() {
    print_step "诊断Docker服务状态..."
    
    print_info "Docker服务状态："
    systemctl status docker.service --no-pager || true
    
    echo ""
    print_info "Docker服务日志（最新20行）："
    journalctl -u docker.service -n 20 --no-pager || true
    
    echo ""
    print_info "系统日志中的Docker相关错误："
    journalctl -xe --no-pager | grep -i docker | tail -10 || true
}

# 检查Docker安装状态
check_docker_installation() {
    print_step "检查Docker安装状态..."
    
    if command -v docker &> /dev/null; then
        print_info "✅ Docker命令已安装"
        print_info "Docker版本: $(docker --version 2>/dev/null || echo '无法获取版本')"
    else
        print_error "❌ Docker命令未找到"
        return 1
    fi
    
    # 检查Docker包
    print_info "已安装的Docker相关包："
    rpm -qa | grep docker || yum list installed | grep docker || true
}

# 检查系统资源
check_system_resources() {
    print_step "检查系统资源..."
    
    print_info "磁盘空间："
    df -h / /var || true
    
    echo ""
    print_info "内存使用："
    free -h || true
    
    echo ""
    print_info "系统负载："
    uptime || true
}

# 检查Docker配置文件
check_docker_config() {
    print_step "检查Docker配置文件..."
    
    if [ -f /etc/docker/daemon.json ]; then
        print_info "Docker daemon配置文件存在："
        cat /etc/docker/daemon.json
        
        # 验证JSON格式
        if python3 -m json.tool /etc/docker/daemon.json > /dev/null 2>&1; then
            print_info "✅ daemon.json格式正确"
        else
            print_error "❌ daemon.json格式错误"
            return 1
        fi
    else
        print_info "Docker daemon配置文件不存在，将创建默认配置"
    fi
}

# 检查Docker数据目录
check_docker_data_dir() {
    print_step "检查Docker数据目录..."
    
    DOCKER_ROOT="/var/lib/docker"
    
    if [ -d "$DOCKER_ROOT" ]; then
        print_info "Docker数据目录存在: $DOCKER_ROOT"
        print_info "目录大小: $(du -sh $DOCKER_ROOT 2>/dev/null || echo '无法获取')"
        print_info "目录权限: $(ls -ld $DOCKER_ROOT)"
    else
        print_warning "Docker数据目录不存在，将创建"
        mkdir -p "$DOCKER_ROOT"
    fi
}

# 清理Docker残留文件
cleanup_docker_files() {
    print_step "清理Docker残留文件..."
    
    # 停止所有Docker相关进程
    print_info "停止Docker相关进程..."
    pkill -f docker || true
    pkill -f containerd || true
    
    # 清理可能的锁文件
    print_info "清理锁文件..."
    rm -f /var/run/docker.sock
    rm -f /var/run/docker.pid
    rm -f /var/run/docker/libcontainerd/containerd.pid
    
    # 清理临时文件
    rm -rf /var/run/docker/*
    rm -rf /tmp/docker*
    
    print_info "清理完成"
}

# 重新配置Docker
reconfigure_docker() {
    print_step "重新配置Docker..."
    
    # 创建Docker配置目录
    mkdir -p /etc/docker
    
    # 创建简化的daemon.json配置
    cat > /etc/docker/daemon.json << 'EOF'
{
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
EOF
    
    print_info "已创建简化的Docker配置"
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    print_info "systemd配置已重新加载"
}

# 检查内核模块
check_kernel_modules() {
    print_step "检查内核模块..."
    
    # 检查overlay模块
    if lsmod | grep -q overlay; then
        print_info "✅ overlay模块已加载"
    else
        print_warning "⚠️  overlay模块未加载，尝试加载..."
        modprobe overlay || print_error "overlay模块加载失败"
    fi
    
    # 检查br_netfilter模块
    if lsmod | grep -q br_netfilter; then
        print_info "✅ br_netfilter模块已加载"
    else
        print_warning "⚠️  br_netfilter模块未加载，尝试加载..."
        modprobe br_netfilter || print_error "br_netfilter模块加载失败"
    fi
}

# 尝试启动Docker服务
try_start_docker() {
    print_step "尝试启动Docker服务..."
    
    # 清理环境
    cleanup_docker_files
    
    # 重新配置
    reconfigure_docker
    
    # 检查内核模块
    check_kernel_modules
    
    # 尝试启动服务
    print_info "启动Docker服务..."
    if systemctl start docker; then
        print_info "✅ Docker服务启动成功"
        
        # 设置开机自启
        systemctl enable docker
        print_info "✅ Docker服务已设置为开机自启"
        
        # 验证服务状态
        sleep 3
        if systemctl is-active --quiet docker; then
            print_info "✅ Docker服务运行正常"
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

# 重新安装Docker
reinstall_docker() {
    print_step "重新安装Docker..."
    
    print_warning "将卸载并重新安装Docker"
    read -p "确认继续？(y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "操作已取消"
        return 1
    fi
    
    # 停止并卸载Docker
    systemctl stop docker || true
    systemctl disable docker || true
    
    yum remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true
    
    # 清理数据目录
    rm -rf /var/lib/docker
    rm -rf /etc/docker
    
    # 重新安装
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 启动服务
    systemctl start docker
    systemctl enable docker
    
    print_info "Docker重新安装完成"
}

# 测试Docker功能
test_docker() {
    print_step "测试Docker功能..."
    
    if docker info &> /dev/null; then
        print_info "✅ Docker info命令正常"
    else
        print_error "❌ Docker info命令失败"
        return 1
    fi
    
    # 运行hello-world测试
    print_info "运行hello-world测试..."
    if docker run --rm hello-world &> /dev/null; then
        print_info "✅ Docker容器运行测试成功"
    else
        print_warning "⚠️  Docker容器运行测试失败"
    fi
    
    return 0
}

# 显示修复结果
show_fix_result() {
    print_step "Docker服务修复结果"
    
    echo "========================================="
    echo "Docker服务状态检查"
    echo "========================================="
    
    if systemctl is-active --quiet docker; then
        echo "✅ Docker服务状态: $(systemctl is-active docker)"
        echo "✅ Docker开机自启: $(systemctl is-enabled docker)"
        echo "✅ Docker版本: $(docker --version)"
        echo ""
        echo "现在可以继续部署CBG项目:"
        echo "  ./deploy/install_docker_compose.sh"
        echo "  ./deploy/docker-deploy.sh --skip-build"
    else
        echo "❌ Docker服务仍然无法启动"
        echo ""
        echo "建议手动操作:"
        echo "1. 查看详细日志: journalctl -u docker.service -f"
        echo "2. 检查系统资源: df -h && free -h"
        echo "3. 重启系统: reboot"
        echo "4. 重新安装Docker: ./deploy/install_docker.sh"
    fi
    echo "========================================="
}

# 主函数
main() {
    print_info "开始诊断和修复Docker服务问题..."
    
    check_root
    diagnose_docker_service
    check_docker_installation
    check_system_resources
    check_docker_config
    check_docker_data_dir
    
    # 尝试修复
    if try_start_docker; then
        test_docker
        show_fix_result
        return 0
    fi
    
    print_warning "标准修复失败，尝试重新安装..."
    if reinstall_docker; then
        test_docker
        show_fix_result
        return 0
    fi
    
    print_error "所有修复方法都失败了"
    show_fix_result
    return 1
}

# 执行主函数
main "$@"
