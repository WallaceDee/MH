# CBG爬虫项目 - Python后端Dockerfile
# 基于Python 3.9官方镜像

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    vim \
    net-tools \
    procps \
    default-libmysqlclient-dev \
    pkg-config \
    chromium \
    chromium-driver \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置Playwright环境变量
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright（使用系统浏览器）
RUN pip install playwright==1.20.0
RUN playwright install-deps

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/output /app/config

# 设置权限
RUN chmod +x /app/run.py /app/src/app.py

# 创建非root用户
RUN useradd -m -u 1000 cbguser && \
    chown -R cbguser:cbguser /app

# 切换到非root用户
USER cbguser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# 启动命令
CMD ["python", "src/app.py"]
