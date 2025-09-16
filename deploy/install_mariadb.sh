#!/bin/bash
# MariaDB 10.11 安装脚本 - Alibaba Cloud Linux 3
# CBG爬虫项目数据库部署脚本（MySQL兼容替代方案）

set -e  # 遇到错误时退出

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
        if [[ "$ID" == "alinux" || "$ID" == "alios" ]]; then
            print_info "检测到 Alibaba Cloud Linux 系统: $PRETTY_NAME"
        else
            print_warning "未检测到Alibaba Cloud Linux，脚本可能需要调整"
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
    yum install -y wget curl vim net-tools lsof
    print_info "依赖工具安装完成"
}

# 安装MariaDB
install_mariadb_server() {
    print_step "安装MariaDB服务器..."
    
    # 安装MariaDB服务器和客户端
    yum install -y mariadb-server mariadb mariadb-devel
    
    print_info "MariaDB安装完成"
}

# 启动MariaDB服务
start_mariadb_service() {
    print_step "启动MariaDB服务..."
    
    # 启动MariaDB服务
    systemctl start mariadb
    systemctl enable mariadb
    
    print_info "MariaDB服务已启动并设置为开机自启"
}

# 安全配置MariaDB
secure_mariadb_installation() {
    print_step "配置MariaDB安全设置..."
    
    # 生成新的root密码
    NEW_ROOT_PASSWORD="CBG_Root_$(date +%Y%m%d)@123"
    
    print_info "设置root密码..."
    
    # MariaDB初始没有密码，直接设置
    mysql -uroot -e "
    UPDATE mysql.user SET Password=PASSWORD('$NEW_ROOT_PASSWORD') WHERE User='root';
    FLUSH PRIVILEGES;
    " 2>/dev/null
    
    # 执行安全配置
    print_info "执行MariaDB安全配置..."
    mysql -uroot -p"$NEW_ROOT_PASSWORD" -e "
    -- 删除匿名用户
    DELETE FROM mysql.user WHERE User='';
    
    -- 禁止root远程登录（可选，根据需要调整）
    DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
    
    -- 删除test数据库
    DROP DATABASE IF EXISTS test;
    DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
    
    -- 刷新权限
    FLUSH PRIVILEGES;
    " 2>/dev/null
    
    print_info "MariaDB安全配置完成"
    echo "新的root密码: $NEW_ROOT_PASSWORD" > /root/mariadb_root_password.txt
    chmod 600 /root/mariadb_root_password.txt
    print_info "root密码已保存到 /root/mariadb_root_password.txt"
}

# 创建CBG项目数据库和用户
create_cbg_database() {
    print_step "创建CBG项目数据库和用户..."
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    CBG_PASSWORD="CBG_User_$(date +%Y%m%d)@456"
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    -- 创建CBG数据库
    CREATE DATABASE IF NOT EXISTS cbg_spider DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    
    -- 创建CBG用户
    CREATE USER IF NOT EXISTS 'cbg_user'@'localhost' IDENTIFIED BY '$CBG_PASSWORD';
    CREATE USER IF NOT EXISTS 'cbg_user'@'%' IDENTIFIED BY '$CBG_PASSWORD';
    
    -- 授权CBG用户访问cbg_spider数据库
    GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'localhost';
    GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
    
    -- 刷新权限
    FLUSH PRIVILEGES;
    
    -- 显示数据库
    SHOW DATABASES;
    " 2>/dev/null
    
    echo "CBG数据库用户密码: $CBG_PASSWORD" > /root/cbg_mariadb_password.txt
    chmod 600 /root/cbg_mariadb_password.txt
    
    print_info "CBG数据库和用户创建完成"
    print_info "数据库名: cbg_spider"
    print_info "用户名: cbg_user"
    print_info "密码已保存到 /root/cbg_mariadb_password.txt"
}

# 配置MariaDB性能参数
configure_mariadb_performance() {
    print_step "优化MariaDB性能配置..."
    
    # 备份原配置文件
    if [ -f /etc/my.cnf ]; then
        cp /etc/my.cnf /etc/my.cnf.backup
    fi
    
    # 创建优化后的配置文件
    cat > /etc/my.cnf << 'EOF'
[mysqld]
# 基本设置
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

# 字符集设置
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 连接设置
max_connections=200
max_connect_errors=10000

# 内存设置（根据服务器内存调整）
innodb_buffer_pool_size=512M
innodb_log_file_size=128M
innodb_log_buffer_size=16M

# 查询缓存
query_cache_size=64M
query_cache_type=1

# 临时表设置
tmp_table_size=64M
max_heap_table_size=64M

# MyISAM设置
key_buffer_size=32M

# 其他优化
innodb_flush_log_at_trx_commit=2
innodb_file_per_table=1

# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/log/mariadb/mariadb-slow.log
long_query_time=2

# 二进制日志
log-bin=mariadb-bin
expire_logs_days=7
max_binlog_size=100M

# SQL模式
sql_mode=STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO

[mysql]
default-character-set=utf8mb4

[client]
default-character-set=utf8mb4
EOF
    
    # 创建日志目录
    mkdir -p /var/log/mariadb
    chown mysql:mysql /var/log/mariadb
    
    print_info "MariaDB配置文件已优化"
}

# 重启MariaDB服务
restart_mariadb_service() {
    print_step "重启MariaDB服务以应用新配置..."
    systemctl restart mariadb
    print_info "MariaDB服务重启完成"
}

# 配置防火墙
configure_firewall() {
    print_step "配置防火墙规则..."
    
    # 检查firewalld是否运行
    if systemctl is-active --quiet firewalld; then
        print_info "配置firewalld规则..."
        firewall-cmd --permanent --add-port=3306/tcp
        firewall-cmd --reload
        print_info "防火墙规则配置完成"
    else
        print_warning "firewalld未运行，请手动配置防火墙规则"
    fi
}

# 显示安装信息
show_installation_info() {
    print_step "MariaDB安装信息汇总"
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt 2>/dev/null || echo "未找到")
    CBG_PASSWORD=$(cat /root/cbg_mariadb_password.txt 2>/dev/null || echo "未找到")
    
    echo "=================================="
    echo "MariaDB (MySQL兼容) 安装完成！"
    echo "=================================="
    echo "服务状态: $(systemctl is-active mariadb)"
    echo "服务端口: 3306"
    echo "数据库类型: MariaDB (完全兼容MySQL)"
    echo ""
    echo "管理员账户:"
    echo "  用户名: root"
    echo "  密码: $ROOT_PASSWORD"
    echo ""
    echo "CBG项目账户:"
    echo "  数据库: cbg_spider"
    echo "  用户名: cbg_user"
    echo "  密码: $CBG_PASSWORD"
    echo ""
    echo "配置文件: /etc/my.cnf"
    echo "数据目录: /var/lib/mysql"
    echo "日志文件: /var/log/mariadb/mariadb.log"
    echo "慢查询日志: /var/log/mariadb/mariadb-slow.log"
    echo ""
    echo "连接示例:"
    echo "  mysql -ucbg_user -p -h localhost cbg_spider"
    echo ""
    echo "Python连接字符串:"
    echo "  mysql+pymysql://cbg_user:$CBG_PASSWORD@localhost:3306/cbg_spider?charset=utf8mb4"
    echo ""
    echo "注意: MariaDB与MySQL完全兼容，您的应用无需修改即可使用"
    echo "=================================="
}

# 主函数
main() {
    print_info "开始安装MariaDB (MySQL兼容数据库)..."
    
    check_root
    check_system
    update_system
    install_dependencies
    install_mariadb_server
    start_mariadb_service
    secure_mariadb_installation
    create_cbg_database
    configure_mariadb_performance
    restart_mariadb_service
    configure_firewall
    show_installation_info
    
    print_info "MariaDB安装完成！"
    print_info "MariaDB与MySQL 100%兼容，您的CBG爬虫项目可以直接使用"
}

# 执行主函数
main "$@"
