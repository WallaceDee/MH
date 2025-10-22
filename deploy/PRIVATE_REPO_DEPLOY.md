# 私有仓库部署指南

## 🔐 私有仓库配置

由于您的项目是私有的，需要配置GitHub访问权限。

## 🚀 方法1：使用SSH密钥（推荐）

### 1. 生成SSH密钥

在服务器上执行：

```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
# 按回车使用默认路径，可以设置密码或直接回车

# 查看公钥
cat ~/.ssh/id_rsa.pub
```

### 2. 添加SSH密钥到GitHub

1. 复制公钥内容
2. 登录GitHub -> Settings -> SSH and GPG keys -> New SSH key
3. 粘贴公钥并保存

### 3. 测试SSH连接

```bash
ssh -T git@github.com
# 应该显示：Hi wallace! You've successfully authenticated...
```

### 4. 克隆私有仓库

```bash
# 使用SSH URL克隆
sudo mkdir -p /usr/lingtong
sudo chown $USER:$USER /usr/lingtong
cd /usr/lingtong
git clone git@github.com:WallaceDee/MH.git .
```

## 🔑 方法2：使用Personal Access Token

### 1. 创建访问令牌

1. 登录GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo` (完整仓库访问)
4. 复制生成的令牌

### 2. 使用令牌克隆

```bash
# 使用令牌克隆（替换YOUR_TOKEN）
sudo mkdir -p /usr/lingtong
sudo chown $USER:$USER /usr/lingtong
cd /usr/lingtong
git clone https://YOUR_TOKEN@github.com/WallaceDee/MH.git .
```

### 3. 配置Git凭据

```bash
# 配置Git记住凭据
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 🔧 更新部署脚本

需要修改部署脚本以使用SSH或令牌：

### 使用SSH的配置

```bash
# 在 auto_deploy.sh 中修改
REPO_URL="git@github.com:WallaceDee/MH.git"
```

### 使用令牌的配置

```bash
# 在 auto_deploy.sh 中修改
REPO_URL="https://YOUR_TOKEN@github.com/WallaceDee/MH.git"
```

## 🚀 完整部署步骤

### 1. 上传项目（选择一种方法）

**SSH方法**：
```bash
# 在服务器上
sudo mkdir -p /usr/lingtong
sudo chown $USER:$USER /usr/lingtong
cd /usr/lingtong
git clone git@github.com:WallaceDee/MH.git .
```

**令牌方法**：
```bash
# 在服务器上
sudo mkdir -p /usr/lingtong
sudo chown $USER:$USER /usr/lingtong
cd /usr/lingtong
git clone https://YOUR_TOKEN@github.com/WallaceDee/MH.git .
```

### 2. 安装自动部署系统

```bash
cd /usr/lingtong
sudo bash deploy/setup_auto_deploy.sh
```

### 3. 配置GitHub Webhook

- URL: `http://lingtong.xyz:9000/webhook`
- 使用安装脚本生成的密钥

## 🔒 安全建议

1. **SSH密钥方法更安全** - 推荐使用
2. **令牌权限最小化** - 只给必要的权限
3. **定期轮换令牌** - 定期更新访问令牌
4. **限制IP访问** - 在GitHub设置中限制访问IP

## 🛠️ 故障排除

### SSH连接问题

```bash
# 检查SSH配置
ssh -vT git@github.com

# 重新生成密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### 令牌问题

```bash
# 测试令牌
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# 检查令牌权限
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user/repos
```

## 📝 后续使用

配置完成后，后续使用相同：

```bash
# 本地开发
git add .
git commit -m "更新功能"
git push origin master

# 系统会自动部署到 lingtong.xyz
```
