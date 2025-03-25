# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，避免Python生成.pyc文件
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 删除不必要的文件目录
RUN rm /app/.env
RUN rm -rf /app/doc
RUN rm -rf /app/conf
RUN rm -rf /app/logs
RUN rm -rf /app/__pycache__
RUN rm -rf /app/test

# 创建必要的文件目录
RUN touch /app/.env
RUN mkdir -p /app/conf

# 安装Python依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 设置默认的配置文件
COPY conf/config.ini /app/conf/

# 设置容器启动命令
CMD ["python", "/app/main_plugin.py"]