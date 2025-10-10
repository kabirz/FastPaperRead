# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y  git npm && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/kabirz/FastPaperRead /tmp/repo && \
    cp -fr /tmp/repo/* . && \
    rm -fr /tmp/repo

# 安装 claude code
RUN npm install -g @anthropic-ai/claude-code

# 安装Python依赖
RUN pip install -r requirements.txt

# 创建必要的目录
RUN mkdir -p uploads output temp

# 暴露端口（如果需要运行Gradio应用）
EXPOSE 7860

# 设置默认命令
CMD ["python", "gradio_app.py"]
