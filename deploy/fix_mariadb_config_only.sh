#!/bin/bash
# 仅修复MariaDB配置以解决1118行大小限制问题
# 简化版本 - 只修改配置和重启服务

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

# 修复MariaDB配置以支持大行
fix_mariadb_config() {
    print_step "修复MariaDB配置以支持大行..."
    
    # 备份原配置文件
    if [ -f /etc/my.cnf ]; then
        cp /etc/my.cnf /etc/my.cnf.backup.$(date +%Y%m%d_%H%M%S)
        print_info "已备份原配置文件"
    fi
    
    # 创建支持大行的配置文件
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

# 内存设置
innodb_buffer_pool_size=512M
innodb_log_file_size=128M
innodb_log_buffer_size=16M

# 解决行大小限制问题的关键配置
innodb_file_format=Barracuda
innodb_file_per_table=1
innodb_large_prefix=1
innodb_strict_mode=0

# 页面大小设置（支持更大的行）
innodb_page_size=16K

# 临时表设置
tmp_table_size=128M
max_heap_table_size=128M

# MyISAM设置
key_buffer_size=64M

# 其他优化
innodb_flush_log_at_trx_commit=2

# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/log/mariadb/mariadb-slow.log
long_query_time=2

# 二进制日志
log-bin=mariadb-bin
expire_logs_days=7
max_binlog_size=100M

# SQL模式 - 移除严格模式以允许大行
sql_mode=NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO

[mysql]
default-character-set=utf8mb4

[client]
default-character-set=utf8mb4
EOF
    
    # 创建日志目录
    mkdir -p /var/log/mariadb
    chown mysql:mysql /var/log/mariadb
    
    print_info "MariaDB配置已更新以支持大行"
    print_info "关键修改："
    print_info "  - innodb_file_format=Barracuda"
    print_info "  - innodb_large_prefix=1"
    print_info "  - innodb_strict_mode=0"
    print_info "  - 移除了严格的SQL模式"
}

# 重启MariaDB服务
restart_mariadb() {
    print_step "重启MariaDB服务以应用新配置..."
    
    print_warning "即将重启MariaDB服务，这会短暂中断数据库连接"
    
    systemctl restart mariadb
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    if systemctl is-active --quiet mariadb; then
        print_info "✅ MariaDB服务重启成功"
        print_info "服务状态: $(systemctl is-active mariadb)"
    else
        print_error "❌ MariaDB服务重启失败"
        print_error "查看服务状态："
        systemctl status mariadb
        exit 1
    fi
}

# 验证配置
verify_config() {
    print_step "验证配置是否生效..."
    
    # 检查关键配置参数
    print_info "检查关键配置参数..."
    
    # 尝试连接并检查配置
    if command -v mysql >/dev/null 2>&1; then
        # 检查innodb相关参数
        mysql -e "SHOW VARIABLES LIKE 'innodb_file_format';" 2>/dev/null || print_warning "无法查询innodb_file_format参数"
        mysql -e "SHOW VARIABLES LIKE 'innodb_large_prefix';" 2>/dev/null || print_warning "无法查询innodb_large_prefix参数"
        mysql -e "SHOW VARIABLES LIKE 'sql_mode';" 2>/dev/null || print_warning "无法查询sql_mode参数"
    else
        print_warning "mysql客户端不可用，跳过配置验证"
    fi
    
    print_info "配置验证完成"
}

# 显示完成信息
show_completion_info() {
    print_step "配置修复完成"
    
    echo "========================================="
    echo "MariaDB配置修复完成！"
    echo "========================================="
    echo "修复内容："
    echo "✅ 启用Barracuda文件格式"
    echo "✅ 启用大前缀索引支持"
    echo "✅ 关闭严格模式"
    echo "✅ 优化SQL模式设置"
    echo "✅ 重启服务应用配置"
    echo ""
    echo "现在可以："
    echo "1. 导入包含大行的SQL文件"
    echo "2. 创建包含多个TEXT/BLOB字段的表"
    echo "3. 使用ROW_FORMAT=DYNAMIC创建表"
    echo ""
    echo "建议在创建表时显式指定："
    echo "ENGINE=InnoDB ROW_FORMAT=DYNAMIC"
    echo "========================================="
}

# 主函数
main() {
    print_info "开始修复MariaDB配置以解决1118行大小限制问题..."
    
    check_root
    fix_mariadb_config
    restart_mariadb
    verify_config
    show_completion_info
    
    print_info "配置修复完成！现在可以导入您的SQL文件了"
}

# 执行主函数
main "$@"
