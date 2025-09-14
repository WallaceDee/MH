# MySQL连接故障排除指南

## 当前问题
- 错误：`Lost connection to MySQL server during query`
- 用户权限错误：`Access denied for user 'cbg_user'@'localhost'`

## 故障排除步骤

### 1. 检查MySQL服务器状态

在MySQL服务器上执行：
```bash
# 检查MySQL服务状态
sudo systemctl status mysql
# 或者
sudo systemctl status mariadb

# 检查端口监听
sudo netstat -tlnp | grep 3306
# 或者
sudo ss -tlnp | grep 3306

# 检查MySQL进程
ps aux | grep mysql
```

### 2. 检查MySQL配置

```bash
# 查看MySQL配置文件
sudo cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep -E "(bind-address|port)"

# 确保配置正确
bind-address = 0.0.0.0
port = 3306
```

### 3. 检查防火墙设置

```bash
# 检查防火墙状态
sudo ufw status
# 或者
sudo firewall-cmd --list-all

# 开放3306端口
sudo ufw allow 3306
# 或者
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

### 4. 检查MySQL用户权限

```sql
-- 登录MySQL
mysql -u root -p

-- 查看所有用户
SELECT User, Host FROM mysql.user;

-- 查看cbg_user权限
SHOW GRANTS FOR 'cbg_user'@'%';
SHOW GRANTS FOR 'cbg_user'@'localhost';

-- 修复权限
DROP USER IF EXISTS 'cbg_user'@'localhost';
DROP USER IF EXISTS 'cbg_user'@'%';
CREATE USER 'cbg_user'@'%' IDENTIFIED BY '447363121';
GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
FLUSH PRIVILEGES;
```

### 5. 检查数据库是否存在

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS cbg_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 测试连接

```bash
# 本地测试
mysql -u root -p

# 远程测试
mysql -h 47.86.33.98 -u root -p

# 测试特定用户
mysql -h 47.86.33.98 -u cbg_user -p cbg_spider
```

## 常见解决方案

### 方案1：重启MySQL服务
```bash
sudo systemctl restart mysql
# 或者
sudo systemctl restart mariadb
```

### 方案2：检查MySQL日志
```bash
# 查看错误日志
sudo tail -f /var/log/mysql/error.log
# 或者
sudo tail -f /var/log/mariadb/mariadb.log
```

### 方案3：重新安装MySQL
```bash
# 停止服务
sudo systemctl stop mysql

# 卸载
sudo apt remove mysql-server mysql-client
# 或者
sudo yum remove mysql-server mysql-client

# 重新安装
sudo apt install mysql-server mysql-client
# 或者
sudo yum install mysql-server mysql-client

# 启动服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 方案4：使用Docker运行MySQL
```bash
# 停止现有MySQL
sudo systemctl stop mysql

# 运行Docker MySQL
sudo docker run --name mysql-server \
  -e MYSQL_ROOT_PASSWORD=447363121 \
  -e MYSQL_DATABASE=cbg_spider \
  -e MYSQL_USER=cbg_user \
  -e MYSQL_PASSWORD=447363121 \
  -p 3306:3306 \
  -d mysql:8.0
```

## 临时解决方案

如果MySQL问题无法快速解决，可以：

1. **继续使用SQLite**
```bash
python start_sqlite.py
```

2. **使用本地MySQL**
   - 在本地安装MySQL
   - 修改配置为localhost

3. **使用其他数据库**
   - PostgreSQL
   - SQLite（当前可用）

## 验证修复

修复后，运行以下测试：

```bash
# 测试连接
python tests/test_simple_mysql.py

# 测试项目启动
python start_mysql.py
```

## 联系支持

如果问题仍然存在，请提供：
1. MySQL服务器操作系统版本
2. MySQL版本
3. 错误日志
4. 网络连接测试结果

