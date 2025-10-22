# SSH连接问题排查指南

## 🔍 问题分析

错误 "Repository not found" 通常有以下几个原因：

1. **SSH密钥未添加到GitHub**
2. **仓库地址不正确**
3. **SSH密钥权限问题**
4. **仓库不存在或权限不足**

## 🛠️ 解决步骤

### 1. 检查SSH密钥是否存在

```bash
# 检查SSH密钥
ls -la ~/.ssh/

# 如果没有密钥，生成一个
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### 2. 查看公钥内容

```bash
# 查看公钥
cat ~/.ssh/id_rsa.pub
```

### 3. 添加SSH密钥到GitHub

1. 复制上面命令输出的公钥内容
2. 登录GitHub -> Settings -> SSH and GPG keys
3. 点击 "New SSH key"
4. 标题：`server-$(hostname)`
5. 粘贴公钥内容
6. 点击 "Add SSH key"

### 4. 测试SSH连接

```bash
# 测试GitHub SSH连接
ssh -T git@github.com

# 应该显示类似：
# Hi wallace! You've successfully authenticated, but GitHub does not provide shell access.
```

### 5. 检查仓库地址

确认仓库地址是否正确：

```bash
# 检查仓库是否存在（需要先配置SSH）
git ls-remote git@github.com:WallaceDee/MH.git

# 或者使用HTTPS方式检查
curl -s https://api.github.com/repos/WallaceDee/MH
```

## 🔧 替代方案：使用HTTPS + 令牌

如果SSH配置有问题，可以使用HTTPS + Personal Access Token：

### 1. 创建Personal Access Token

1. GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo` (完整仓库访问)
4. 复制生成的令牌

### 2. 使用令牌克隆

```bash
# 使用令牌克隆（替换YOUR_TOKEN）
git clone https://YOUR_TOKEN@github.com/WallaceDee/MH.git

# 或者先克隆再配置凭据
git clone https://github.com/WallaceDee/MH.git
cd MH
git remote set-url origin https://YOUR_TOKEN@github.com/WallaceDee/MH.git
```

### 3. 配置Git凭据存储

```bash
# 配置Git记住凭据
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 🚀 快速解决方案

### 方案1：修复SSH

```bash
# 1. 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# 2. 查看公钥
cat ~/.ssh/id_rsa.pub

# 3. 添加到GitHub（手动操作）

# 4. 测试连接
ssh -T git@github.com

# 5. 重新克隆
git clone git@github.com:WallaceDee/MH.git
```

### 方案2：使用HTTPS

```bash
# 1. 创建Personal Access Token（在GitHub上）

# 2. 使用令牌克隆
git clone https://YOUR_TOKEN@github.com/WallaceDee/MH.git

# 3. 更新部署脚本使用HTTPS URL
```

## 📝 更新部署脚本

如果使用HTTPS方式，需要更新部署脚本：

```bash
# 编辑 auto_deploy.sh
REPO_URL="https://YOUR_TOKEN@github.com/WallaceDee/MH.git"

# 编辑 quick_deploy.sh
REPO_URL="https://YOUR_TOKEN@github.com/WallaceDee/MH.git"
```

## 🔍 调试命令

```bash
# 检查SSH配置
ssh -vT git@github.com

# 检查Git配置
git config --list

# 检查远程仓库
git remote -v

# 测试仓库访问
git ls-remote origin
```
