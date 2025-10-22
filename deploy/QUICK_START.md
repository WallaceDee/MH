# CBG项目快速部署指南 - lingtong.xyz

## 🚀 一键部署

### 1. 在服务器上运行安装脚本

```bash
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

### 3. 访问应用

- **主应用**: http://lingtong.xyz
- **API接口**: http://lingtong.xyz/api/v1
- **Webhook状态**: http://lingtong.xyz:9000/status

## 🔧 手动部署

```bash
# 完整部署
/usr/lingtong/deploy/auto_deploy.sh deploy

# 快速部署
/usr/lingtong/deploy/quick_deploy.sh

# 查看状态
/usr/lingtong/deploy/auto_deploy.sh status

# 回滚
/usr/lingtong/deploy/auto_deploy.sh rollback
```

## 📊 架构说明

- **Flask应用**: 端口5000，服务前端静态文件和API
- **Webhook服务**: 端口9000，监听GitHub推送事件
- **域名**: lingtong.xyz
- **自动部署**: 推送代码到GitHub自动触发部署

## ✨ 特性

- ✅ 完全自动化部署
- ✅ 自动备份和回滚
- ✅ 健康检查
- ✅ 详细日志记录
- ✅ 无需nginx，Flask直接服务静态文件
