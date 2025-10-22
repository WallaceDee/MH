#!/bin/bash
# CBG爬虫项目Docker部署脚本
# 连接到现有MariaDB数据库

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

# 检查Docker和Docker Compose
check_docker() {
    print_step "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose（支持插件版本和独立版本）
    if docker compose version &> /dev/null; then
        print_info "Docker Compose插件已安装: $(docker compose version --short)"
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        print_info "Docker Compose独立版本已安装: $(docker-compose --version)"
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        print_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    print_info "Docker环境检查通过"
    print_info "Docker版本: $(docker --version)"
}

# 检查MariaDB连接
check_mariadb() {
    print_step "检查MariaDB数据库连接..."
    
    # 检查MariaDB服务状态
    if ! systemctl is-active --quiet mariadb; then
        print_error "MariaDB服务未运行，请启动MariaDB服务"
        print_info "启动命令: sudo systemctl start mariadb"
        exit 1
    fi
    
    # 检查密码文件
    if [ ! -f /root/cbg_mariadb_password.txt ]; then
        print_error "未找到MariaDB密码文件: /root/cbg_mariadb_password.txt"
        print_info "请先运行setup_mariadb_passwords.sh设置密码"
        exit 1
    fi
    
    # 测试数据库连接
    DB_PASSWORD=$(cat /root/cbg_mariadb_password.txt)
    if mysql -ulingtong -p"$DB_PASSWORD" -D cbg_spider -e "SELECT 1;" &> /dev/null; then
        print_info "MariaDB连接测试成功"
    else
        print_error "MariaDB连接测试失败，请检查数据库配置"
        exit 1
    fi
}

# 创建必要的目录
create_directories() {
    print_step "创建必要的目录..."
    
    mkdir -p data logs output config
    mkdir -p logs/nginx
    mkdir -p deploy/nginx/conf.d
    
    # 设置目录权限
    chmod 755 data logs output config
    
    print_info "目录创建完成"
}

# 构建前端应用
build_frontend() {
    print_step "构建Vue.js前端应用..."
    
    if [ -d "web" ]; then
        cd web
        
        # 检查Node.js环境
        if command -v npm &> /dev/null; then
            print_info "使用npm构建前端..."
            npm install
            npm run build
        elif command -v yarn &> /dev/null; then
            print_info "使用yarn构建前端..."
            yarn install
            yarn build
        else
            print_warning "未找到npm或yarn，将在Docker中构建前端"
        fi
        
        cd ..
        print_info "前端构建完成"
    else
        print_warning "未找到web目录，跳过前端构建"
    fi
}

# 更新应用配置
update_app_config() {
    print_step "更新应用配置..."
    
    # 创建环境变量文件
    cat > .env << EOF
# 数据库配置
DB_HOST=host.docker.internal
DB_PORT=3306
DB_NAME=cbg_spider
DB_USER=cbg_user

# Flask配置
FLASK_ENV=production
FLASK_APP=src/app.py

# 应用配置
LOG_LEVEL=INFO
MAX_WORKERS=4
SPIDER_DELAY_MIN=5
SPIDER_DELAY_MAX=8
EOF
    
    print_info "应用配置更新完成"
}

# 部署Docker容器
deploy_containers() {
    print_step "部署Docker容器..."
    
    # 停止现有容器
    print_info "停止现有容器..."
    $COMPOSE_CMD -f docker-compose.prod.yml down || true
    
    # 构建镜像
    print_info "构建Docker镜像..."
    $COMPOSE_CMD -f docker-compose.prod.yml build
    
    # 启动容器
    print_info "启动容器..."
    $COMPOSE_CMD -f docker-compose.prod.yml up -d
    
    # 等待容器启动
    print_info "等待容器启动..."
    sleep 10
    
    print_info "容器部署完成"
}

# 检查部署状态
check_deployment() {
    print_step "检查部署状态..."
    
    # 检查容器状态
    print_info "容器状态:"
    $COMPOSE_CMD -f docker-compose.prod.yml ps
    
    # 检查服务健康状态
    print_info "等待服务就绪..."
    sleep 20
    
    # 测试API服务
    if curl -f http://localhost:5000/api/v1/system/health &> /dev/null; then
        print_info "✅ API服务健康检查通过"
    else
        print_warning "⚠️  API服务健康检查失败，请检查日志"
    fi
    
    print_info "部署状态检查完成"
}

# 显示部署信息
show_deployment_info() {
    print_step "部署完成信息"
    
    echo "========================================="
    echo "CBG爬虫项目Docker部署完成！"
    echo "========================================="
    echo "服务访问地址:"
    echo "  API接口:  http://localhost:5000/api/v1"
    echo "  健康检查: http://localhost:5000/api/v1/system/health"
    echo ""
    echo "容器管理命令:"
    echo "  查看状态: $COMPOSE_CMD -f docker-compose.prod.yml ps"
    echo "  查看日志: $COMPOSE_CMD -f docker-compose.prod.yml logs -f"
    echo "  停止服务: $COMPOSE_CMD -f docker-compose.prod.yml down"
    echo "  重启服务: $COMPOSE_CMD -f docker-compose.prod.yml restart"
    echo ""
    echo "数据库连接:"
    echo "  容器连接宿主机MariaDB: host.docker.internal:3306"
    echo "  数据库名: cbg_spider"
    echo "  用户名: lingtong"
    echo ""
    echo "日志文件位置:"
    echo "  应用日志: ./logs/"
    echo "  容器日志: docker-compose logs"
    echo "========================================="
}

# 显示帮助信息
show_help() {
    echo "CBG爬虫项目Docker部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  --skip-build   跳过前端构建"
    echo "  --dev          使用开发环境配置"
    echo ""
    echo "示例:"
    echo "  $0              # 完整部署"
    echo "  $0 --skip-build # 跳过前端构建"
}

# 主函数
main() {
    local skip_build=false
    local dev_mode=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            --dev)
                dev_mode=true
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "开始CBG爬虫项目Docker部署..."
    
    check_docker
    check_mariadb
    create_directories
    
    if [ "$skip_build" = false ]; then
        build_frontend
    else
        print_info "跳过前端构建"
    fi
    
    update_app_config
    deploy_containers
    check_deployment
    show_deployment_info
    
    print_info "Docker部署完成！"
}

# 执行主函数
main "$@"
