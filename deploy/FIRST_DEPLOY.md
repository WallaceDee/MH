# 首次部署步骤 - lingtong.xyz

## 🚀 第一步：上传项目到服务器

### 方法1：使用Git克隆（推荐）

在服务器上执行：

```bash
# 创建项目目录
sudo mkdir -p /usr/lingtong
sudo chown $USER:$USER /usr/lingtong

# 克隆项目
cd /usr/lingtong
git clone https://github.com/wallace/MH.git .

# 设置权限
sudo chmod +x deploy/*.sh
sudo chmod +x deploy/webhook_deploy.py
```

### 方法2：上传压缩包

1. 在本地打包项目：
```bash
# 在项目根目录执行
tar -czf MH.tar.gz --exclude=node_modules --exclude=.git --exclude=__pycache__ .
```

2. 上传到服务器：
```bash
# 使用scp上传
scp MH.tar.gz root@lingtong.xyz:/tmp/

# 在服务器上解压
sudo mkdir -p /usr/lingtong
cd /usr/lingtong
sudo tar -xzf /tmp/MH.tar.gz
sudo chown -R $USER:$USER /usr/lingtong
```

## 🔧 第二步：安装自动部署系统

```bash
# 在服务器上执行
cd /usr/lingtong
sudo bash deploy/setup_auto_deploy.sh
```

## 🌐 第三步：配置GitHub Webhook

1. 登录GitHub，进入 `wallace/MH` 仓库
2. 点击 `Settings` -> `Webhooks` -> `Add webhook`
3. 配置如下：
   - **Payload URL**: `http://lingtong.xyz:9000/webhook`
   - **Content type**: `application/json`
   - **Secret**: 使用安装脚本显示的密钥
   - **Events**: 选择 `Just the push event`
   - **Active**: 勾选

## ✅ 第四步：测试部署

```bash
# 手动触发部署测试
/usr/lingtong/deploy/auto_deploy.sh deploy

# 检查服务状态
/usr/lingtong/deploy/auto_deploy.sh status
```

## 🌐 访问应用

- **主应用**: http://lingtong.xyz
- **API接口**: http://lingtong.xyz/api/v1
- **Webhook状态**: http://lingtong.xyz:9000/status

## 📝 后续使用

以后只需要推送代码到GitHub，系统会自动部署：

```bash
# 本地开发完成后
git add .
git commit -m "更新功能"
git push origin master

# 系统会自动拉取代码并部署到 lingtong.xyz
```
