#!/bin/bash
# MariaDB连接测试脚本
# 诊断Docker部署时的数据库连接问题

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

# 检查MariaDB服务状态
check_mariadb_service() {
    print_step "检查MariaDB服务状态..."
    
    if systemctl is-active --quiet mariadb; then
        print_info "✅ MariaDB服务正在运行"
        print_info "服务状态: $(systemctl is-active mariadb)"
    else
        print_error "❌ MariaDB服务未运行"
        print_info "尝试启动MariaDB服务..."
        systemctl start mariadb || {
            print_error "MariaDB服务启动失败"
            systemctl status mariadb
            return 1
        }
    fi
    
    # 检查端口监听
    if netstat -tlnp | grep -q :3306; then
        print_info "✅ MariaDB端口3306正在监听"
        netstat -tlnp | grep :3306
    else
        print_warning "⚠️  端口3306未监听"
    fi
}

# 检查密码文件
check_password_files() {
    print_step "检查密码文件..."
    
    # 检查root密码文件
    if [ -f /root/mariadb_root_password.txt ]; then
        print_info "✅ MariaDB root密码文件存在"
        ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
        print_info "root密码长度: ${#ROOT_PASSWORD} 字符"
    elif [ -f /root/mysql_root_password.txt ]; then
        print_info "✅ MySQL root密码文件存在"
        ROOT_PASSWORD=$(cat /root/mysql_root_password.txt)
        print_info "root密码长度: ${#ROOT_PASSWORD} 字符"
    else
        print_error "❌ 未找到root密码文件"
        print_info "请检查以下位置："
        print_info "  - /root/mariadb_root_password.txt"
        print_info "  - /root/mysql_root_password.txt"
        return 1
    fi
    
    # 检查CBG用户密码文件
    if [ -f /root/cbg_mariadb_password.txt ]; then
        print_info "✅ CBG用户密码文件存在"
        CBG_PASSWORD=$(cat /root/cbg_mariadb_password.txt)
        print_info "CBG用户密码长度: ${#CBG_PASSWORD} 字符"
    elif [ -f /root/cbg_mysql_password.txt ]; then
        print_info "✅ CBG用户密码文件存在（MySQL格式）"
        CBG_PASSWORD=$(cat /root/cbg_mysql_password.txt)
        print_info "CBG用户密码长度: ${#CBG_PASSWORD} 字符"
    else
        print_error "❌ 未找到CBG用户密码文件"
        print_info "请检查以下位置："
        print_info "  - /root/cbg_mariadb_password.txt"
        print_info "  - /root/cbg_mysql_password.txt"
        return 1
    fi
}

# 测试root用户连接
test_root_connection() {
    print_step "测试root用户连接..."
    
    if [ -z "$ROOT_PASSWORD" ]; then
        print_error "root密码为空"
        return 1
    fi
    
    print_info "尝试连接MariaDB..."
    if mysql -uroot -p"$ROOT_PASSWORD" -e "SELECT 1 as test;" 2>/dev/null; then
        print_info "✅ root用户连接成功"
        
        # 显示数据库版本
        MYSQL_VERSION=$(mysql -uroot -p"$ROOT_PASSWORD" -e "SELECT VERSION();" -s --skip-column-names 2>/dev/null)
        print_info "数据库版本: $MYSQL_VERSION"
        
        return 0
    else
        print_error "❌ root用户连接失败"
        print_info "尝试查看详细错误..."
        mysql -uroot -p"$ROOT_PASSWORD" -e "SELECT 1;" 2>&1 || true
        return 1
    fi
}

# 检查CBG数据库和用户
check_cbg_database() {
    print_step "检查CBG数据库和用户..."
    
    # 检查数据库是否存在
    if mysql -uroot -p"$ROOT_PASSWORD" -e "USE cbg_spider; SELECT 1;" &>/dev/null; then
        print_info "✅ cbg_spider数据库存在"
    else
        print_error "❌ cbg_spider数据库不存在"
        print_info "创建cbg_spider数据库..."
        mysql -uroot -p"$ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS cbg_spider DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || {
            print_error "创建数据库失败"
            return 1
        }
        print_info "✅ cbg_spider数据库已创建"
    fi
    
    # 检查CBG用户是否存在
    CBG_USER_EXISTS=$(mysql -uroot -p"$ROOT_PASSWORD" -e "SELECT COUNT(*) FROM mysql.user WHERE User='cbg_user';" -s --skip-column-names 2>/dev/null)
    if [ "$CBG_USER_EXISTS" -gt 0 ]; then
        print_info "✅ cbg_user用户存在"
    else
        print_error "❌ cbg_user用户不存在"
        if [ -n "$CBG_PASSWORD" ]; then
            print_info "创建cbg_user用户..."
            mysql -uroot -p"$ROOT_PASSWORD" -e "
                CREATE USER IF NOT EXISTS 'cbg_user'@'localhost' IDENTIFIED BY '$CBG_PASSWORD';
                CREATE USER IF NOT EXISTS 'cbg_user'@'%' IDENTIFIED BY '$CBG_PASSWORD';
                GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'localhost';
                GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
                FLUSH PRIVILEGES;
            " || {
                print_error "创建用户失败"
                return 1
            }
            print_info "✅ cbg_user用户已创建"
        else
            print_error "CBG用户密码为空，无法创建用户"
            return 1
        fi
    fi
}

# 测试CBG用户连接
test_cbg_connection() {
    print_step "测试CBG用户连接..."
    
    if [ -z "$CBG_PASSWORD" ]; then
        print_error "CBG用户密码为空"
        return 1
    fi
    
    print_info "尝试使用cbg_user连接cbg_spider数据库..."
    if mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "SELECT 1 as test;" 2>/dev/null; then
        print_info "✅ CBG用户连接成功"
        
        # 测试权限
        if mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "SHOW TABLES;" &>/dev/null; then
            print_info "✅ CBG用户权限正常"
        else
            print_warning "⚠️  CBG用户权限可能有问题"
        fi
        
        return 0
    else
        print_error "❌ CBG用户连接失败"
        print_info "尝试查看详细错误..."
        mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "SELECT 1;" 2>&1 || true
        return 1
    fi
}

# 检查网络连接
check_network() {
    print_step "检查网络连接..."
    
    # 测试本地回环连接
    if nc -z localhost 3306 2>/dev/null; then
        print_info "✅ localhost:3306 可连接"
    else
        print_warning "⚠️  localhost:3306 连接失败"
    fi
    
    # 测试127.0.0.1连接
    if nc -z 127.0.0.1 3306 2>/dev/null; then
        print_info "✅ 127.0.0.1:3306 可连接"
    else
        print_warning "⚠️  127.0.0.1:3306 连接失败"
    fi
    
    # 检查防火墙状态
    if systemctl is-active --quiet firewalld; then
        print_info "防火墙状态: 运行中"
        if firewall-cmd --list-ports | grep -q 3306; then
            print_info "✅ 防火墙已开放3306端口"
        else
            print_warning "⚠️  防火墙未开放3306端口"
        fi
    else
        print_info "防火墙状态: 未运行"
    fi
}

# 显示连接配置信息
show_connection_info() {
    print_step "连接配置信息"
    
    echo "========================================="
    echo "MariaDB连接配置信息"
    echo "========================================="
    echo "服务状态: $(systemctl is-active mariadb)"
    echo "端口监听: $(netstat -tlnp | grep :3306 | wc -l) 个连接"
    echo ""
    echo "数据库连接信息:"
    echo "  主机: localhost / 127.0.0.1"
    echo "  端口: 3306"
    echo "  数据库: cbg_spider"
    echo "  用户名: cbg_user"
    echo "  密码文件: /root/cbg_mariadb_password.txt"
    echo ""
    echo "Docker连接字符串:"
    if [ -n "$CBG_PASSWORD" ]; then
        echo "  mysql+pymysql://cbg_user:$CBG_PASSWORD@host.docker.internal:3306/cbg_spider?charset=utf8mb4"
    else
        echo "  mysql+pymysql://cbg_user:密码@host.docker.internal:3306/cbg_spider?charset=utf8mb4"
    fi
    echo ""
    echo "测试命令:"
    echo "  mysql -ucbg_user -p -h localhost -D cbg_spider"
    echo "========================================="
}

# 修复常见问题
fix_common_issues() {
    print_step "尝试修复常见问题..."
    
    # 重置CBG用户密码
    if [ -n "$ROOT_PASSWORD" ] && [ -n "$CBG_PASSWORD" ]; then
        print_info "重置CBG用户密码..."
        mysql -uroot -p"$ROOT_PASSWORD" -e "
            DROP USER IF EXISTS 'cbg_user'@'localhost';
            DROP USER IF EXISTS 'cbg_user'@'%';
            CREATE USER 'cbg_user'@'localhost' IDENTIFIED BY '$CBG_PASSWORD';
            CREATE USER 'cbg_user'@'%' IDENTIFIED BY '$CBG_PASSWORD';
            GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'localhost';
            GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
            FLUSH PRIVILEGES;
        " && print_info "✅ CBG用户密码重置完成" || print_error "❌ 密码重置失败"
    fi
}

# 主函数
main() {
    print_info "开始MariaDB连接诊断..."
    
    # 检查root权限
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    check_mariadb_service
    check_password_files
    
    if test_root_connection; then
        check_cbg_database
        if ! test_cbg_connection; then
            print_warning "CBG用户连接失败，尝试修复..."
            fix_common_issues
            test_cbg_connection
        fi
    else
        print_error "root用户连接失败，无法继续测试"
    fi
    
    check_network
    show_connection_info
    
    print_info "MariaDB连接诊断完成"
}

# 执行主函数
main "$@"
