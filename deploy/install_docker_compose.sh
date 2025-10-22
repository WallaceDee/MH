#!/bin/bash
# Docker Compose安装脚本 - Alibaba Cloud Linux 3
# 适用于已安装Docker但缺少Docker Compose的情况

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

# 检查Docker是否已安装
check_docker() {
    print_step "检查Docker安装状态..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        print_info "运行: ./deploy/install_docker.sh"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker服务未运行，请启动Docker服务"
        print_info "运行: sudo systemctl start docker"
        exit 1
    fi
    
    print_info "Docker已安装并运行正常"
    print_info "Docker版本: $(docker --version)"
}

# 检查现有的Docker Compose
check_existing_compose() {
    print_step "检查现有Docker Compose..."
    
    # 检查Docker Compose插件
    if docker compose version &> /dev/null; then
        print_info "Docker Compose插件已安装: $(docker compose version)"
        return 0
    fi
    
    # 检查独立的docker-compose
    if command -v docker-compose &> /dev/null; then
        print_info "Docker Compose独立版本已安装: $(docker-compose --version)"
        return 0
    fi
    
    print_warning "未找到Docker Compose，需要安装"
    return 1
}

# 安装Docker Compose插件（推荐方式）
install_compose_plugin() {
    print_step "安装Docker Compose插件..."
    
    # 对于较新的Docker版本，Compose应该已经作为插件安装
    # 尝试安装compose插件
    if yum list installed | grep -q docker-compose-plugin; then
        print_info "Docker Compose插件已通过yum安装"
    else
        print_info "尝试通过yum安装Docker Compose插件..."
        yum install -y docker-compose-plugin || {
            print_warning "yum安装失败，尝试其他方法"
            return 1
        }
    fi
    
    # 验证插件安装
    if docker compose version &> /dev/null; then
        print_info "✅ Docker Compose插件安装成功"
        print_info "版本: $(docker compose version)"
        return 0
    else
        return 1
    fi
}

# 安装独立的Docker Compose
install_standalone_compose() {
    print_step "安装独立的Docker Compose..."
    
    # 获取最新版本号
    DOCKER_COMPOSE_VERSION="2.24.1"
    
    print_info "下载Docker Compose v${DOCKER_COMPOSE_VERSION}..."
    
    # 下载Docker Compose二进制文件
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接到系统PATH
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # 验证安装
    if command -v docker-compose &> /dev/null; then
        print_info "✅ Docker Compose独立版本安装成功"
        print_info "版本: $(docker-compose --version)"
        return 0
    else
        print_error "Docker Compose安装验证失败"
        return 1
    fi
}

# 使用国内镜像安装（备用方案）
install_compose_china_mirror() {
    print_step "使用国内镜像安装Docker Compose..."
    
    DOCKER_COMPOSE_VERSION="2.24.1"
    
    print_info "从DaoCloud镜像下载..."
    
    # 使用DaoCloud镜像
    curl -L "https://get.daocloud.io/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # 验证安装
    if command -v docker-compose &> /dev/null; then
        print_info "✅ Docker Compose安装成功（国内镜像）"
        print_info "版本: $(docker-compose --version)"
        return 0
    else
        return 1
    fi
}

# pip安装方式（最后备用）
install_compose_pip() {
    print_step "使用pip安装Docker Compose..."
    
    # 检查pip是否可用
    if ! command -v pip3 &> /dev/null; then
        print_info "安装pip..."
        yum install -y python3-pip
    fi
    
    # 使用pip安装
    pip3 install docker-compose
    
    # 验证安装
    if command -v docker-compose &> /dev/null; then
        print_info "✅ Docker Compose安装成功（pip方式）"
        print_info "版本: $(docker-compose --version)"
        return 0
    else
        return 1
    fi
}

# 测试Docker Compose
test_compose() {
    print_step "测试Docker Compose..."
    
    # 创建临时测试文件
    cat > /tmp/test-compose.yml << 'EOF'
version: '3.8'
services:
  test:
    image: hello-world
EOF
    
    cd /tmp
    
    # 测试docker compose命令
    if docker compose -f test-compose.yml config &> /dev/null; then
        print_info "✅ Docker Compose插件测试成功"
        COMPOSE_CMD="docker compose"
    elif docker-compose -f test-compose.yml config &> /dev/null; then
        print_info "✅ Docker Compose独立版本测试成功"
        COMPOSE_CMD="docker-compose"
    else
        print_error "❌ Docker Compose测试失败"
        return 1
    fi
    
    # 清理测试文件
    rm -f /tmp/test-compose.yml
    
    print_info "推荐使用命令: $COMPOSE_CMD"
    return 0
}

# 创建docker-compose命令别名
create_compose_alias() {
    print_step "创建Docker Compose命令别名..."
    
    # 如果只有插件版本，创建docker-compose别名
    if docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        cat > /usr/local/bin/docker-compose << 'EOF'
#!/bin/bash
exec docker compose "$@"
EOF
        chmod +x /usr/local/bin/docker-compose
        print_info "已创建docker-compose -> docker compose别名"
    fi
}

# 显示安装结果
show_installation_result() {
    print_step "Docker Compose安装结果"
    
    echo "========================================="
    echo "Docker Compose安装完成！"
    echo "========================================="
    
    # 显示可用的命令
    if docker compose version &> /dev/null; then
        echo "✅ Docker Compose插件: $(docker compose version)"
        echo "   使用命令: docker compose"
    fi
    
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose独立版本: $(docker-compose --version)"
        echo "   使用命令: docker-compose"
    fi
    
    echo ""
    echo "常用命令:"
    echo "  docker-compose up -d          # 启动服务"
    echo "  docker-compose down           # 停止服务"
    echo "  docker-compose ps             # 查看容器状态"
    echo "  docker-compose logs -f        # 查看日志"
    echo ""
    echo "现在可以运行CBG项目部署:"
    echo "  ./deploy/docker-deploy.sh --skip-build"
    echo "========================================="
}

# 主函数
main() {
    print_info "开始安装Docker Compose..."
    
    check_root
    check_docker
    
    # 如果已经安装，直接退出
    if check_existing_compose; then
        print_info "Docker Compose已安装，无需重复安装"
        show_installation_result
        return 0
    fi
    
    # 尝试多种安装方式
    print_info "尝试安装Docker Compose..."
    
    # 方法1: 安装插件版本
    if install_compose_plugin; then
        create_compose_alias
        test_compose
        show_installation_result
        return 0
    fi
    
    print_warning "插件安装失败，尝试独立版本..."
    
    # 方法2: 安装独立版本
    if install_standalone_compose; then
        test_compose
        show_installation_result
        return 0
    fi
    
    print_warning "GitHub下载失败，尝试国内镜像..."
    
    # 方法3: 国内镜像
    if install_compose_china_mirror; then
        test_compose
        show_installation_result
        return 0
    fi
    
    print_warning "二进制安装失败，尝试pip安装..."
    
    # 方法4: pip安装
    if install_compose_pip; then
        test_compose
        show_installation_result
        return 0
    fi
    
    # 所有方法都失败
    print_error "所有安装方法都失败了"
    print_error "请手动安装Docker Compose:"
    echo ""
    echo "手动安装命令:"
    echo "curl -L \"https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "chmod +x /usr/local/bin/docker-compose"
    echo "ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose"
    
    exit 1
}

# 执行主函数
main "$@"
