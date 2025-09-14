# MySQL用户权限修复指南

## 问题描述
错误：`ERROR 1045 (28000): Access denied for user 'cbg_user'@'localhost' (using password: YES)`

## 解决方案

### 方法1：在MySQL服务器上修复权限

1. **登录MySQL服务器**
```bash
mysql -u root -p
```

2. **执行权限修复脚本**
```sql
-- 检查当前用户
SELECT User, Host FROM mysql.user WHERE User = 'cbg_user';

-- 删除可能存在的用户
DROP USER IF EXISTS 'cbg_user'@'localhost';
DROP USER IF EXISTS 'cbg_user'@'%';

-- 创建新用户，允许从任何IP连接
CREATE USER 'cbg_user'@'%' IDENTIFIED BY '447363121';

-- 授权所有权限给cbg_spider数据库
GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证用户创建
SELECT User, Host FROM mysql.user WHERE User = 'cbg_user';
```

### 方法2：使用root用户连接

如果无法修复权限，可以临时使用root用户：

1. **修改配置文件**
```bash
# 编辑 config.env
MYSQL_USER=root
MYSQL_PASSWORD=你的root密码
```

2. **或者修改测试脚本**
```python
# 在测试脚本中临时使用root用户
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = '你的root密码'
```

### 方法3：检查MySQL配置

1. **检查MySQL是否允许远程连接**
```bash
# 查看MySQL配置文件
cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep bind-address
```

2. **确保bind-address设置为0.0.0.0**
```ini
bind-address = 0.0.0.0
```

3. **重启MySQL服务**
```bash
sudo systemctl restart mysql
# 或者
sudo systemctl restart mariadb
```

## 测试连接

修复后，使用以下命令测试连接：

```bash
# 测试连接
mysql -h 47.86.33.98 -u cbg_user -p cbg_spider
```

## 常见问题

### 1. 用户存在但权限不足
```sql
-- 重新授权
GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
FLUSH PRIVILEGES;
```

### 2. 用户只能从localhost连接
```sql
-- 删除localhost用户，创建%用户
DROP USER 'cbg_user'@'localhost';
CREATE USER 'cbg_user'@'%' IDENTIFIED BY '447363121';
GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';
FLUSH PRIVILEGES;
```

### 3. 数据库不存在
```sql
-- 创建数据库
CREATE DATABASE cbg_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 验证步骤

1. **检查用户权限**
```sql
SHOW GRANTS FOR 'cbg_user'@'%';
```

2. **测试连接**
```bash
mysql -h 47.86.33.98 -u cbg_user -p cbg_spider -e "SELECT 1;"
```

3. **运行项目测试**
```bash
python tests/test_simple_mysql.py
```

