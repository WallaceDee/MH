#!/bin/bash
# MariaDB密码设置脚本 - 用于已安装但缺少密码配置的MariaDB
# CBG爬虫项目数据库配置脚本

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

# 检查MariaDB服务状态
check_mariadb_service() {
    print_step "检查MariaDB服务状态..."
    
    if ! systemctl is-active --quiet mariadb; then
        print_error "MariaDB服务未运行，请先启动服务"
        print_info "启动命令: systemctl start mariadb"
        exit 1
    fi
    
    print_info "MariaDB服务运行正常"
}

# 尝试确定当前root密码状态
check_root_password_status() {
    print_step "检查root密码状态..."
    
    # 尝试无密码登录
    if mysql -uroot -e "SELECT 1;" 2>/dev/null; then
        print_info "root用户当前无密码，可以直接登录"
        return 0
    else
        print_warning "root用户已设置密码"
        return 1
    fi
}

# 设置root密码
setup_root_password() {
    print_step "设置root密码..."
    
    NEW_ROOT_PASSWORD="CBG_Root_$(date +%Y%m%d)@123"
    
    if check_root_password_status; then
        # 无密码状态，直接设置
        print_info "为root用户设置新密码..."
        mysql -uroot -e "
        SET PASSWORD FOR 'root'@'localhost' = PASSWORD('$NEW_ROOT_PASSWORD');
        FLUSH PRIVILEGES;
        " 2>/dev/null
    else
        # 已有密码，需要用户输入当前密码
        print_warning "root用户已有密码，请输入当前密码来重置"
        echo -n "请输入当前root密码: "
        read -s CURRENT_PASSWORD
        echo
        
        if mysql -uroot -p"$CURRENT_PASSWORD" -e "SELECT 1;" 2>/dev/null; then
            print_info "密码验证成功，设置新密码..."
            mysql -uroot -p"$CURRENT_PASSWORD" -e "
            SET PASSWORD FOR 'root'@'localhost' = PASSWORD('$NEW_ROOT_PASSWORD');
            FLUSH PRIVILEGES;
            " 2>/dev/null
        else
            print_error "密码验证失败，请检查输入的密码是否正确"
            exit 1
        fi
    fi
    
    # 保存新密码
    echo "$NEW_ROOT_PASSWORD" > /root/mariadb_root_password.txt
    chmod 600 /root/mariadb_root_password.txt
    
    print_info "root密码已设置并保存到 /root/mariadb_root_password.txt"
    print_info "新的root密码: $NEW_ROOT_PASSWORD"
}

# 创建CBG数据库和用户
setup_cbg_database() {
    print_step "设置CBG项目数据库和用户..."
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    CBG_PASSWORD="447363121"
    
    print_info "创建CBG数据库和用户..."
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    -- 创建CBG数据库
    CREATE DATABASE IF NOT EXISTS cbg_spider DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    
    -- 删除可能存在的旧用户
    DROP USER IF EXISTS 'cbg_user'@'localhost';
    DROP USER IF EXISTS 'cbg_user'@'%';
    DROP USER IF EXISTS 'lingtong'@'localhost';
    DROP USER IF EXISTS 'lingtong'@'%';
    
    -- 创建CBG用户
    CREATE USER 'lingtong'@'localhost' IDENTIFIED BY '$CBG_PASSWORD';
    CREATE USER 'lingtong'@'%' IDENTIFIED BY '$CBG_PASSWORD';
    
    -- 授权CBG用户访问cbg_spider数据库
    GRANT ALL PRIVILEGES ON cbg_spider.* TO 'lingtong'@'localhost';
    GRANT ALL PRIVILEGES ON cbg_spider.* TO 'lingtong'@'%';
    
    -- 刷新权限
    FLUSH PRIVILEGES;
    " 2>/dev/null
    
    # 保存CBG用户密码
    echo "$CBG_PASSWORD" > /root/cbg_mariadb_password.txt
    chmod 600 /root/cbg_mariadb_password.txt
    
    print_info "CBG数据库和用户创建完成"
    print_info "数据库名: cbg_spider"
    print_info "用户名: lingtong"
    print_info "密码已保存到 /root/cbg_mariadb_password.txt"
}

# 执行安全配置
secure_mariadb() {
    print_step "执行MariaDB安全配置..."
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    -- 删除匿名用户
    DELETE FROM mysql.user WHERE User='';
    
    -- 禁止root远程登录（保留本地登录）
    DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
    
    -- 删除test数据库
    DROP DATABASE IF EXISTS test;
    DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
    
    -- 刷新权限
    FLUSH PRIVILEGES;
    " 2>/dev/null
    
    print_info "MariaDB安全配置完成"
}

# 优化MariaDB配置
optimize_mariadb_config() {
    print_step "优化MariaDB配置..."
    
    # 备份原配置文件
    if [ -f /etc/my.cnf ]; then
        cp /etc/my.cnf /etc/my.cnf.backup.$(date +%Y%m%d_%H%M%S)
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
    
    print_info "MariaDB配置已优化"
    print_warning "需要重启MariaDB服务以应用新配置"
}

# 重启MariaDB服务
restart_mariadb() {
    print_step "重启MariaDB服务..."
    
    print_warning "即将重启MariaDB服务，这会短暂中断数据库连接"
    read -p "确认重启？(y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl restart mariadb
        print_info "MariaDB服务重启完成"
        
        # 验证服务状态
        if systemctl is-active --quiet mariadb; then
            print_info "MariaDB服务运行正常"
        else
            print_error "MariaDB服务重启失败，请检查配置"
            systemctl status mariadb
        fi
    else
        print_info "跳过重启，配置将在下次重启时生效"
    fi
}

# 测试连接
test_connection() {
    print_step "测试数据库连接..."
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    CBG_PASSWORD=$(cat /root/cbg_mariadb_password.txt)
    
    # 测试root连接
    if mysql -uroot -p"$ROOT_PASSWORD" -e "SELECT 'Root connection OK' as status;" 2>/dev/null; then
        print_info "✅ root用户连接测试成功"
    else
        print_error "❌ root用户连接测试失败"
    fi
    
    # 测试CBG用户连接
    if mysql -ulingtong -p"$CBG_PASSWORD" -D cbg_spider -e "SELECT 'CBG user connection OK' as status;" 2>/dev/null; then
        print_info "✅ lingtong用户连接测试成功"
    else
        print_error "❌ lingtong用户连接测试失败"
    fi
}

# 显示配置信息
show_final_info() {
    print_step "MariaDB配置完成信息"
    
    ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    CBG_PASSWORD=$(cat /root/cbg_mariadb_password.txt)
    
    echo "========================================="
    echo "MariaDB配置完成！"
    echo "========================================="
    echo "数据库类型: MariaDB (MySQL 100%兼容)"
    echo "服务状态: $(systemctl is-active mariadb)"
    echo "服务端口: 3306"
    echo ""
    echo "管理员账户:"
    echo "  用户名: root"
    echo "  密码: $ROOT_PASSWORD"
    echo "  密码文件: /root/mariadb_root_password.txt"
    echo ""
    echo "CBG项目账户:"
    echo "  数据库: cbg_spider"
    echo "  用户名: lingtong"
    echo "  密码: $CBG_PASSWORD"
    echo "  密码文件: /root/cbg_mariadb_password.txt"
    echo ""
    echo "Python连接字符串:"
    echo "  mysql+pymysql://lingtong:$CBG_PASSWORD@localhost:3306/cbg_spider?charset=utf8mb4"
    echo ""
    echo "管理命令:"
    echo "  ./mariadb_management.sh status    # 查看状态"
    echo "  ./mariadb_management.sh info      # 查看数据库信息"
    echo "  ./mariadb_management.sh backup    # 备份数据库"
    echo "  ./mariadb_management.sh help      # 查看所有命令"
    echo ""
    echo "注意: MariaDB与MySQL完全兼容，可以使用mysql命令连接"
    echo "========================================="
}

# 主函数
main() {
    print_info "开始配置MariaDB密码和CBG项目数据库..."
    
    check_root
    check_mariadb_service
    setup_root_password
    setup_cbg_database
    secure_mariadb
    
    # 测试密码设置是否成功（不需要重启）
    print_step "测试密码设置..."
    test_connection
    
    # 询问是否要优化配置（需要重启）
    echo ""
    print_warning "密码设置已完成，无需重启！"
    print_info "以下操作是可选的配置优化："
    read -p "是否要优化MariaDB配置文件？(这需要重启服务) (y/N): " -r
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        optimize_mariadb_config
        restart_mariadb
        print_info "配置优化完成"
    else
        print_info "跳过配置优化，使用默认配置"
    fi
    
    show_final_info
    
    print_info "MariaDB配置完成！现在可以使用mariadb_management.sh脚本管理数据库"
}

# 执行主函数
main "$@"
