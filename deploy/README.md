# CBG项目自动部署系统

## 📋 概述

这套自动部署系统可以让您从GitHub自动拉取代码并部署，无需手动上传代码。

## 🚀 快速开始

### 1. 安装自动部署系统

```bash
# 在服务器上运行
sudo bash deploy/setup_auto_deploy.sh
```

### 2. 配置GitHub Webhook

1. 登录GitHub，进入您的仓库
2. 点击 `Settings` -> `Webhooks` -> `Add webhook`
3. 配置如下：
   - **Payload URL**: `http://lingtong.xyz:9000/webhook`
   - **Content type**: `application/json`
   - **Secret**: 使用安装脚本显示的密钥
   - **Events**: 选择 `Just the push event`
   - **Active**: 勾选

### 3. 测试部署

推送代码到GitHub，系统会自动触发部署。

## 📁 文件说明

### 核心脚本

- `auto_deploy.sh` - 完整自动部署脚本
- `quick_deploy.sh` - 快速部署脚本
- `webhook_deploy.py` - GitHub Webhook服务
- `setup_auto_deploy.sh` - 安装配置脚本

### 配置文件

- `webhook-deploy.service` - 系统服务配置
- `.env` - 环境变量配置

## 🔧 使用方法

### 手动部署

```bash
# 完整部署（包含备份）
./deploy/auto_deploy.sh deploy

# 快速部署
./deploy/quick_deploy.sh
```

### 管理服务

```bash
# 查看状态
./deploy/auto_deploy.sh status

# 查看日志
./deploy/auto_deploy.sh logs

# 回滚到上一个版本
./deploy/auto_deploy.sh rollback
```

### Webhook服务管理

```bash
# 启动服务
sudo systemctl start webhook-deploy

# 停止服务
sudo systemctl stop webhook-deploy

# 查看状态
sudo systemctl status webhook-deploy

# 查看日志
sudo journalctl -u webhook-deploy -f
```

## ⚙️ 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# GitHub Webhook配置
GITHUB_WEBHOOK_SECRET=your-webhook-secret
REPO_NAME=WallaceDee/MH
BRANCH=master

# 部署配置
PROJECT_DIR=/usr/lingtong
DEPLOY_SCRIPT=/usr/lingtong/deploy/auto_deploy.sh
LOG_FILE=/var/log/webhook_deploy.log
```

### 修改仓库地址

编辑 `auto_deploy.sh` 文件：

```bash
REPO_URL="https://github.com/WallaceDee/MH.git"
BRANCH="master"
```

## 🔍 监控和日志

### 查看部署日志

```bash
# 查看Webhook服务日志
sudo journalctl -u webhook-deploy -f

# 查看部署脚本日志
tail -f /var/log/webhook_deploy.log

# 查看应用日志
./deploy/auto_deploy.sh logs
```

### 健康检查

```bash
# 检查Webhook服务
curl http://lingtong.xyz:9000/status

# 检查应用状态
curl http://lingtong.xyz/api/v1/system/health
```

## 🛠️ 故障排除

### 常见问题

1. **Webhook不触发**
   - 检查GitHub Webhook配置
   - 检查服务器防火墙设置
   - 查看Webhook服务日志

2. **部署失败**
   - 检查GitHub仓库权限
   - 检查Docker服务状态
   - 查看部署脚本日志

3. **服务无法启动**
   - 检查端口占用
   - 检查文件权限
   - 查看系统服务日志

### 调试命令

```bash
# 检查服务状态
sudo systemctl status webhook-deploy

# 检查端口占用
netstat -tlnp | grep 9000

# 检查文件权限
ls -la /opt/cbg-spider/deploy/

# 手动测试Webhook
curl -X POST http://localhost:9000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"ref":"refs/heads/master","repository":{"full_name":"your-username/MH"}}'
```

## 📊 部署流程

1. **代码推送** → GitHub触发Webhook
2. **Webhook接收** → 验证签名和分支
3. **备份当前版本** → 创建备份
4. **停止服务** → 停止当前容器
5. **拉取代码** → 从GitHub拉取最新代码
6. **构建镜像** → Docker构建新镜像
7. **启动服务** → 启动新容器
8. **健康检查** → 验证服务状态
9. **清理资源** → 清理旧镜像

## 🔒 安全说明

- Webhook使用HMAC-SHA256签名验证
- 支持HTTPS加密传输
- 自动备份防止数据丢失
- 回滚功能确保系统稳定

## 📞 支持

如有问题，请检查：
1. 系统日志
2. 服务状态
3. 网络连接
4. 文件权限
