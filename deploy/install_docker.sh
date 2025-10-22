#!/bin/bash
# Docker和Docker Compose安装脚本 - Alibaba Cloud Linux 3
# CBG爬虫项目容器化部署准备脚本

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

# 检查系统版本
check_system() {
    print_step "检查系统版本..."
    
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        print_info "系统信息: $PRETTY_NAME"
        
        if [[ "$ID" == "alinux" || "$ID" == "alios" ]]; then
            print_info "检测到Alibaba Cloud Linux系统"
        else
            print_warning "非Alibaba Cloud Linux系统，脚本可能需要调整"
        fi
    else
        print_warning "无法检测系统版本"
    fi
}

# 更新系统包
update_system() {
    print_step "更新系统包..."
    yum update -y
    print_info "系统包更新完成"
}

# 安装必要的工具
install_dependencies() {
    print_step "安装依赖工具..."
    yum install -y \
        yum-utils \
        device-mapper-persistent-data \
        lvm2 \
        curl \
        wget \
        vim \
        net-tools \
        htop
    print_info "依赖工具安装完成"
}

# 卸载旧版本Docker
remove_old_docker() {
    print_step "卸载旧版本Docker..."
    yum remove -y \
        docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-engine \
        podman \
        runc || true
    print_info "旧版本Docker卸载完成"
}

# 添加Docker官方仓库
add_docker_repo() {
    print_step "添加Docker官方仓库..."
    
    # 添加Docker CE仓库
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # 导入GPG密钥
    rpm --import https://download.docker.com/linux/centos/gpg
    
    print_info "Docker仓库添加完成"
}

# 安装Docker CE
install_docker() {
    print_step "安装Docker CE..."
    
    # 安装Docker CE
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    print_info "Docker CE安装完成"
}

# 启动并配置Docker服务
configure_docker() {
    print_step "配置Docker服务..."
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    # 验证Docker安装
    if docker --version; then
        print_info "Docker安装验证成功"
    else
        print_error "Docker安装验证失败"
        exit 1
    fi
    
    # 运行hello-world测试
    print_info "运行Docker测试..."
    if docker run hello-world; then
        print_info "Docker测试运行成功"
    else
        print_warning "Docker测试运行失败，但Docker已安装"
    fi
    
    print_info "Docker服务配置完成"
}

# 安装Docker Compose
install_docker_compose() {
    print_step "安装Docker Compose..."
    
    # 检查是否已通过插件安装
    if docker compose version &> /dev/null; then
        print_info "Docker Compose插件已安装"
        return 0
    fi
    
    # 下载并安装Docker Compose
    DOCKER_COMPOSE_VERSION="2.23.3"
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # 验证安装
    if docker-compose --version; then
        print_info "Docker Compose安装验证成功"
    else
        print_error "Docker Compose安装验证失败"
        exit 1
    fi
    
    print_info "Docker Compose安装完成"
}

# 配置Docker优化设置
optimize_docker() {
    print_step "优化Docker配置..."
    
    # 创建Docker配置目录
    mkdir -p /etc/docker
    
    # 创建Docker daemon配置文件
    cat > /etc/docker/daemon.json << 'EOF'
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ],
    "storage-driver": "overlay2",
    "storage-opts": [
        "overlay2.override_kernel_check=true"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "live-restore": true,
    "exec-opts": ["native.cgroupdriver=systemd"],
    "default-ulimits": {
        "nofile": {
            "Name": "nofile",
            "Hard": 64000,
            "Soft": 64000
        }
    }
}
EOF
    
    # 重启Docker服务以应用配置
    systemctl daemon-reload
    systemctl restart docker
    
    print_info "Docker配置优化完成"
}

# 配置防火墙
configure_firewall() {
    print_step "配置防火墙..."
    
    if systemctl is-active --quiet firewalld; then
        print_info "配置firewalld规则..."
        
        # 开放Docker相关端口
        firewall-cmd --permanent --add-port=80/tcp      # HTTP
        firewall-cmd --permanent --add-port=443/tcp     # HTTPS
        firewall-cmd --permanent --add-port=5000/tcp    # Flask API
        firewall-cmd --permanent --add-port=8080/tcp    # 备用端口
        
        # 允许Docker网络
        firewall-cmd --permanent --zone=trusted --add-interface=docker0
        
        # 重载防火墙规则
        firewall-cmd --reload
        
        print_info "防火墙配置完成"
    else
        print_warning "firewalld未运行，请手动配置防火墙规则"
    fi
}

# 创建Docker用户组
setup_docker_group() {
    print_step "配置Docker用户组..."
    
    # 创建docker用户组（通常已存在）
    groupadd docker 2>/dev/null || true
    
    # 将当前用户添加到docker组
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker "$SUDO_USER"
        print_info "用户 $SUDO_USER 已添加到docker组"
    fi
    
    print_info "Docker用户组配置完成"
    print_warning "需要重新登录才能生效，或使用 'newgrp docker' 命令"
}

# 显示安装信息
show_installation_info() {
    print_step "Docker安装信息汇总"
    
    echo "========================================="
    echo "Docker安装完成！"
    echo "========================================="
    echo "Docker版本: $(docker --version)"
    echo "Docker Compose版本: $(docker-compose --version 2>/dev/null || docker compose version)"
    echo "Docker服务状态: $(systemctl is-active docker)"
    echo "Docker开机自启: $(systemctl is-enabled docker)"
    echo ""
    echo "常用Docker命令:"
    echo "  docker --version              # 查看Docker版本"
    echo "  docker info                   # 查看Docker信息"
    echo "  docker ps                     # 查看运行中的容器"
    echo "  docker images                 # 查看镜像列表"
    echo "  docker-compose up -d          # 启动服务"
    echo "  docker-compose down           # 停止服务"
    echo "  docker-compose logs -f        # 查看日志"
    echo ""
    echo "CBG项目部署:"
    echo "  cd /path/to/cbg-project"
    echo "  ./deploy/docker-deploy.sh"
    echo ""
    echo "配置文件位置:"
    echo "  Docker配置: /etc/docker/daemon.json"
    echo "  Docker服务: /etc/systemd/system/docker.service"
    echo ""
    echo "注意事项:"
    echo "1. 如需非root用户使用Docker，请重新登录或执行 'newgrp docker'"
    echo "2. Docker镜像仓库已配置国内镜像源，加速下载"
    echo "3. 已开放常用端口，如需其他端口请手动配置防火墙"
    echo "========================================="
}

# 测试Docker安装
test_docker_installation() {
    print_step "测试Docker安装..."
    
    # 拉取测试镜像
    print_info "拉取nginx测试镜像..."
    docker pull nginx:alpine
    
    # 运行测试容器
    print_info "运行测试容器..."
    docker run --name test-nginx -d -p 8888:80 nginx:alpine
    
    # 等待容器启动
    sleep 5
    
    # 测试容器访问
    if curl -f http://localhost:8888 &> /dev/null; then
        print_info "✅ Docker测试成功！"
        
        # 清理测试容器
        docker stop test-nginx
        docker rm test-nginx
        docker rmi nginx:alpine
        
        print_info "测试容器已清理"
    else
        print_warning "⚠️  Docker测试失败，但Docker已安装"
    fi
}

# 主函数
main() {
    print_info "开始安装Docker和Docker Compose..."
    
    check_root
    check_system
    update_system
    install_dependencies
    remove_old_docker
    add_docker_repo
    install_docker
    configure_docker
    install_docker_compose
    optimize_docker
    configure_firewall
    setup_docker_group
    test_docker_installation
    show_installation_info
    
    print_info "Docker安装完成！现在可以部署CBG爬虫项目了"
}

# 执行主函数
main "$@"
