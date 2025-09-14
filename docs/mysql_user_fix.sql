-- MySQL用户权限修复脚本
-- 请在MySQL服务器上以root用户执行

-- 1. 检查当前用户
SELECT User, Host FROM mysql.user WHERE User = 'cbg_user';

-- 2. 删除可能存在的用户（如果存在）
DROP USER IF EXISTS 'cbg_user'@'localhost';
DROP USER IF EXISTS 'cbg_user'@'%';

-- 3. 创建新用户，允许从任何IP连接
CREATE USER 'cbg_user'@'%' IDENTIFIED BY '447363121';

-- 4. 授权所有权限给cbg_spider数据库
GRANT ALL PRIVILEGES ON cbg_spider.* TO 'cbg_user'@'%';

-- 5. 刷新权限
FLUSH PRIVILEGES;

-- 6. 验证用户创建
SELECT User, Host FROM mysql.user WHERE User = 'cbg_user';

-- 7. 测试连接（可选）
-- SHOW GRANTS FOR 'cbg_user'@'%';

