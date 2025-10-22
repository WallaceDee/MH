#!/bin/bash
# MariaDB管理脚本 - CBG爬虫项目
# 提供常用的MariaDB管理功能（MySQL兼容）

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

# 获取MariaDB密码
get_mariadb_passwords() {
    if [ -f /root/mariadb_root_password.txt ]; then
        ROOT_PASSWORD=$(cat /root/mariadb_root_password.txt)
    elif [ -f /root/mysql_root_password.txt ]; then
        # 兼容从MySQL迁移的情况
        ROOT_PASSWORD=$(cat /root/mysql_root_password.txt)
        print_warning "使用MySQL密码文件，建议重新设置密码"
    else
        print_error "未找到root密码文件"
        exit 1
    fi
    
    if [ -f /root/cbg_mariadb_password.txt ]; then
        CBG_PASSWORD=$(cat /root/cbg_mariadb_password.txt)
    elif [ -f /root/cbg_mysql_password.txt ]; then
        # 兼容从MySQL迁移的情况
        CBG_PASSWORD=$(cat /root/cbg_mysql_password.txt)
        print_warning "使用MySQL CBG密码文件，建议重新设置密码"
    else
        print_warning "未找到CBG用户密码文件"
        CBG_PASSWORD=""
    fi
}

# 显示MariaDB状态
show_mariadb_status() {
    print_step "MariaDB服务状态"
    echo "服务状态: $(systemctl is-active mariadb)"
    echo "开机自启: $(systemctl is-enabled mariadb)"
    echo "进程信息:"
    ps aux | grep mariadb | grep -v grep || echo "  未找到MariaDB进程"
    echo "端口监听:"
    netstat -tlnp | grep :3306 || echo "  3306端口未监听"
    echo ""
}

# 显示数据库信息
show_database_info() {
    print_step "数据库信息"
    get_mariadb_passwords
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    SELECT 
        SCHEMA_NAME as '数据库名',
        DEFAULT_CHARACTER_SET_NAME as '字符集',
        DEFAULT_COLLATION_NAME as '排序规则'
    FROM information_schema.SCHEMATA 
    WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys');
    " 2>/dev/null
    echo ""
}

# 显示用户信息
show_user_info() {
    print_step "用户信息"
    get_mariadb_passwords
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    SELECT 
        User as '用户名',
        Host as '主机',
        Password != '' as '有密码'
    FROM mysql.user 
    WHERE User != ''
    ORDER BY User, Host;
    " 2>/dev/null
    echo ""
}

# 显示CBG数据库表信息
show_cbg_tables() {
    print_step "CBG数据库表信息"
    get_mariadb_passwords
    
    if [ -z "$CBG_PASSWORD" ]; then
        print_error "CBG用户密码未找到，无法查询表信息"
        return
    fi
    
    mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "
    SELECT 
        TABLE_NAME as '表名',
        TABLE_ROWS as '行数',
        ROUND(DATA_LENGTH/1024/1024, 2) as '数据大小(MB)',
        ROUND(INDEX_LENGTH/1024/1024, 2) as '索引大小(MB)',
        CREATE_TIME as '创建时间'
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'cbg_spider'
    ORDER BY TABLE_NAME;
    " 2>/dev/null || print_error "查询CBG表信息失败"
    echo ""
}

# 备份CBG数据库
backup_cbg_database() {
    print_step "备份CBG数据库"
    get_mariadb_passwords
    
    BACKUP_DIR="/var/backups/mariadb"
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/cbg_spider_$(date +%Y%m%d_%H%M%S).sql"
    
    print_info "开始备份数据库到: $BACKUP_FILE"
    mysqldump -uroot -p"$ROOT_PASSWORD" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --hex-blob \
        cbg_spider > "$BACKUP_FILE"
    
    # 压缩备份文件
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    print_info "备份完成: $BACKUP_FILE"
    print_info "备份文件大小: $(du -h $BACKUP_FILE | cut -f1)"
    
    # 清理7天前的备份
    find "$BACKUP_DIR" -name "cbg_spider_*.sql.gz" -mtime +7 -delete
    print_info "已清理7天前的旧备份文件"
}

# 恢复CBG数据库
restore_cbg_database() {
    if [ -z "$1" ]; then
        print_error "请指定备份文件路径"
        echo "用法: $0 restore <备份文件路径>"
        return 1
    fi
    
    BACKUP_FILE="$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "备份文件不存在: $BACKUP_FILE"
        return 1
    fi
    
    print_step "恢复CBG数据库"
    get_mariadb_passwords
    
    print_warning "此操作将覆盖现有的cbg_spider数据库！"
    read -p "确认继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "操作已取消"
        return 0
    fi
    
    print_info "开始恢复数据库从: $BACKUP_FILE"
    
    # 如果是压缩文件，先解压
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        print_info "解压备份文件..."
        TEMP_FILE="/tmp/cbg_restore_$(date +%s).sql"
        gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
        RESTORE_FILE="$TEMP_FILE"
    else
        RESTORE_FILE="$BACKUP_FILE"
    fi
    
    # 删除并重新创建数据库
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    DROP DATABASE IF EXISTS cbg_spider;
    CREATE DATABASE cbg_spider DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    " 2>/dev/null
    
    # 恢复数据
    mysql -uroot -p"$ROOT_PASSWORD" cbg_spider < "$RESTORE_FILE"
    
    # 清理临时文件
    if [ -f "$TEMP_FILE" ]; then
        rm -f "$TEMP_FILE"
    fi
    
    print_info "数据库恢复完成"
}

# 优化CBG数据库
optimize_cbg_database() {
    print_step "优化CBG数据库"
    get_mariadb_passwords
    
    if [ -z "$CBG_PASSWORD" ]; then
        print_error "CBG用户密码未找到"
        return
    fi
    
    print_info "开始优化数据库表..."
    
    # 获取所有表名
    TABLES=$(mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "SHOW TABLES;" -s --skip-column-names 2>/dev/null)
    
    for table in $TABLES; do
        print_info "优化表: $table"
        mysql -ucbg_user -p"$CBG_PASSWORD" -D cbg_spider -e "OPTIMIZE TABLE $table;" 2>/dev/null
    done
    
    print_info "数据库优化完成"
}

# 查看MariaDB错误日志
show_mariadb_error_log() {
    print_step "MariaDB错误日志 (最新50行)"
    
    # 尝试多个可能的日志文件位置
    LOG_FILES=(
        "/var/log/mariadb/mariadb.log"
        "/var/log/mariadb.log" 
        "/var/log/mysqld.log"
    )
    
    for log_file in "${LOG_FILES[@]}"; do
        if [ -f "$log_file" ]; then
            print_info "日志文件: $log_file"
            tail -n 50 "$log_file"
            return 0
        fi
    done
    
    print_error "未找到错误日志文件"
}

# 查看MariaDB慢查询日志
show_mariadb_slow_log() {
    print_step "MariaDB慢查询日志 (最新20条)"
    
    # 尝试多个可能的慢查询日志位置
    SLOW_LOG_FILES=(
        "/var/log/mariadb/mariadb-slow.log"
        "/var/log/mariadb-slow.log"
        "/var/log/mysql-slow.log"
    )
    
    for log_file in "${SLOW_LOG_FILES[@]}"; do
        if [ -f "$log_file" ]; then
            print_info "慢查询日志文件: $log_file"
            tail -n 100 "$log_file" | grep -A 5 -B 5 "Query_time" | tail -n 50
            return 0
        fi
    done
    
    print_warning "慢查询日志文件不存在或未启用"
}

# 显示MariaDB配置
show_mariadb_config() {
    print_step "MariaDB重要配置参数"
    get_mariadb_passwords
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    SHOW VARIABLES WHERE Variable_name IN (
        'character_set_server',
        'collation_server', 
        'max_connections',
        'innodb_buffer_pool_size',
        'query_cache_size',
        'slow_query_log',
        'long_query_time',
        'version'
    );
    " 2>/dev/null
}

# 重置CBG用户密码
reset_cbg_password() {
    print_step "重置CBG用户密码"
    get_mariadb_passwords
    
    NEW_CBG_PASSWORD="CBG_User_$(date +%Y%m%d_%H%M%S)@789"
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    UPDATE mysql.user SET Password=PASSWORD('$NEW_CBG_PASSWORD') WHERE User='cbg_user';
    FLUSH PRIVILEGES;
    " 2>/dev/null
    
    echo "$NEW_CBG_PASSWORD" > /root/cbg_mariadb_password.txt
    chmod 600 /root/cbg_mariadb_password.txt
    
    print_info "CBG用户密码已重置"
    print_info "新密码: $NEW_CBG_PASSWORD"
    print_info "密码已保存到 /root/cbg_mariadb_password.txt"
}

# 显示版本信息
show_version_info() {
    print_step "数据库版本信息"
    get_mariadb_passwords
    
    mysql -uroot -p"$ROOT_PASSWORD" -e "
    SELECT 
        VERSION() as '数据库版本',
        @@version_comment as '版本说明';
    " 2>/dev/null
    
    echo ""
    print_info "MariaDB与MySQL完全兼容，可以使用mysql命令连接"
}

# 显示帮助信息
show_help() {
    echo "MariaDB管理脚本 - CBG爬虫项目"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "可用命令:"
    echo "  status      - 显示MariaDB服务状态"
    echo "  info        - 显示数据库和用户信息"
    echo "  tables      - 显示CBG数据库表信息"
    echo "  backup      - 备份CBG数据库"
    echo "  restore     - 恢复CBG数据库 (需要备份文件路径)"
    echo "  optimize    - 优化CBG数据库"
    echo "  error-log   - 查看MariaDB错误日志"
    echo "  slow-log    - 查看MariaDB慢查询日志"
    echo "  config      - 显示MariaDB配置"
    echo "  reset-pwd   - 重置CBG用户密码"
    echo "  version     - 显示数据库版本信息"
    echo "  help        - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status"
    echo "  $0 backup"
    echo "  $0 restore /var/backups/mariadb/cbg_spider_20240101_120000.sql.gz"
    echo ""
    echo "注意: MariaDB与MySQL 100%兼容，可以使用mysql命令连接"
}

# 主函数
main() {
    case "${1:-help}" in
        "status")
            show_mariadb_status
            ;;
        "info")
            show_database_info
            show_user_info
            ;;
        "tables")
            show_cbg_tables
            ;;
        "backup")
            backup_cbg_database
            ;;
        "restore")
            restore_cbg_database "$2"
            ;;
        "optimize")
            optimize_cbg_database
            ;;
        "error-log")
            show_mariadb_error_log
            ;;
        "slow-log")
            show_mariadb_slow_log
            ;;
        "config")
            show_mariadb_config
            ;;
        "reset-pwd")
            reset_cbg_password
            ;;
        "version")
            show_version_info
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
