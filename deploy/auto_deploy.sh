#!/bin/bash

# CBG项目自动化部署脚本
# 从GitHub拉取最新代码并自动构建部署

set -e  # 遇到错误立即退出

# 配置变量
REPO_URL="git@github.com:WallaceDee/MH.git"
BRANCH="master"  # 要部署的分支
PROJECT_DIR="/usr/lingtong"  # 项目部署目录
BACKUP_DIR="/usr/backups/lingtong"  # 备份目录
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
CONTAINER_NAME="cbg-spider-app"

# 颜色输出
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 检查Docker Compose命令
check_docker_compose() {
    if command -v "docker-compose" &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        log_error "Docker Compose 命令未找到，请先安装"
        exit 1
    fi
    log_info "使用Docker Compose命令: $DOCKER_COMPOSE_CMD"
}

# 检查必要的命令
check_commands() {
    log_info "检查必要命令..."
    check_command "git"
    check_command "docker"
    check_docker_compose
    log_success "所有必要命令检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$BACKUP_DIR"
    log_success "目录创建完成"
}

# 备份当前版本
backup_current() {
    if [ -d "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/$DOCKER_COMPOSE_FILE" ]; then
        log_info "备份当前版本..."
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        cp -r "$PROJECT_DIR" "$BACKUP_DIR/$BACKUP_NAME"
        log_success "当前版本已备份到: $BACKUP_DIR/$BACKUP_NAME"
    else
        log_warning "未找到当前版本，跳过备份"
    fi
}

# 停止当前服务
stop_services() {
    log_info "停止当前服务..."
    if [ -f "$PROJECT_DIR/$DOCKER_COMPOSE_FILE" ]; then
        cd "$PROJECT_DIR"
        $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" down || true
        log_success "服务已停止"
    else
        log_warning "未找到docker-compose文件，跳过停止服务"
    fi
}

# 拉取最新代码
pull_code() {
    log_info "从GitHub拉取最新代码..."
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        # 如果目录已存在，拉取更新
        cd "$PROJECT_DIR"
        git fetch origin
        git reset --hard origin/$BRANCH
        git clean -fd
        log_success "代码更新完成"
    else
        # 如果目录不存在，克隆仓库
        log_info "首次部署，克隆仓库..."
        git clone -b "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
        log_success "代码克隆完成"
    fi
}

# 构建和启动服务
build_and_start() {
    log_info "构建和启动服务..."
    cd "$PROJECT_DIR"
    
    # 构建镜像
    log_info "构建Docker镜像..."
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 30
    
    # 检查容器状态
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_success "容器运行正常"
    else
        log_error "容器启动失败"
        return 1
    fi
    
    # 检查API健康状态
    if curl -f http://localhost/api/v1/system/health > /dev/null 2>&1; then
        log_success "API健康检查通过"
    else
        log_warning "API健康检查失败，但容器正在运行"
    fi
}

# 清理旧镜像
cleanup_images() {
    log_info "清理未使用的Docker镜像..."
    docker image prune -f
    log_success "镜像清理完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo ""
    echo "=========================================="
    echo "  CBG项目部署信息"
    echo "=========================================="
    echo "  项目地址: http://localhost"
    echo "  API地址: http://localhost/api/v1"
    echo "  项目目录: $PROJECT_DIR"
    echo "  备份目录: $BACKUP_DIR"
    echo "  容器名称: $CONTAINER_NAME"
    echo "=========================================="
    echo ""
    
    # 显示容器状态
    log_info "当前容器状态:"
    docker ps | grep "$CONTAINER_NAME" || echo "  未找到运行中的容器"
}

# 回滚到上一个版本
rollback() {
    log_warning "执行回滚操作..."
    
    # 停止当前服务
    stop_services
    
    # 查找最新的备份
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -n1)
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "未找到备份文件，无法回滚"
        exit 1
    fi
    
    log_info "回滚到备份: $LATEST_BACKUP"
    
    # 恢复备份
    rm -rf "$PROJECT_DIR"
    cp -r "$BACKUP_DIR/$LATEST_BACKUP" "$PROJECT_DIR"
    
    # 启动服务
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "回滚完成"
}

# 显示帮助信息
show_help() {
    echo "CBG项目自动化部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  deploy    执行部署（默认）"
    echo "  rollback  回滚到上一个版本"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy    # 执行部署"
    echo "  $0 rollback  # 回滚到上一个版本"
    echo "  $0 status    # 查看服务状态"
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    echo ""
    echo "容器状态:"
    docker ps | grep "$CONTAINER_NAME" || echo "  未找到运行中的容器"
    echo ""
    echo "服务日志 (最近20行):"
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker logs --tail 20 "$CONTAINER_NAME"
    else
        echo "  容器未运行"
    fi
}

# 查看服务日志
show_logs() {
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker logs -f "$CONTAINER_NAME"
    else
        log_error "容器未运行"
        exit 1
    fi
}

# 主函数
main() {
    local action=${1:-deploy}
    
    case $action in
        deploy)
            log_info "开始执行自动部署..."
            check_commands
            create_directories
            backup_current
            stop_services
            pull_code
            build_and_start
            health_check
            cleanup_images
            show_deployment_info
            ;;
        rollback)
            rollback
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help)
            show_help
            ;;
        *)
            log_error "未知选项: $action"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
