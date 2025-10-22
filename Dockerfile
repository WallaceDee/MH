# CBG爬虫项目 - 全栈Dockerfile with Playwright + Vue.js
# 使用Microsoft官方Playwright镜像作为基础镜像

FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production
ENV NODE_VERSION=18

# 设置工作目录
WORKDIR /app

# 安装Node.js和npm（用于构建前端）
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs

# 安装额外的系统依赖
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    pkg-config \
    vim \
    net-tools \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 构建前端
WORKDIR /app/web
RUN npm install --production=false
RUN npm run build

# 回到项目根目录
WORKDIR /app

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/output /app/config

# 设置权限
RUN chmod +x /app/run.py /app/src/app.py

# 容器内以root用户运行（简化权限管理）
# RUN useradd -m cbguser && chown -R cbguser:cbguser /app
# USER cbguser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/system/health || exit 1

# 启动命令
CMD ["python", "src/app.py"]
