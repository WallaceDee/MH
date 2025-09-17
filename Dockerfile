# CBG爬虫项目 - Python后端Dockerfile with Playwright
# 使用Microsoft官方Playwright镜像

FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# 设置工作目录
WORKDIR /app

# 安装额外的系统依赖
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    pkg-config \
    vim \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

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
