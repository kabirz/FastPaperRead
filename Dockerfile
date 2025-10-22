# 使用Python 3.11作为基础镜像
FROM docker.1ms.run/python:3.11-slim

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
    cp -fr /tmp/repo/.claude . && \
    rm -fr /tmp/repo

# 安装 claude code
RUN npm install -g @anthropic-ai/claude-code

# 安装Python依赖
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# 创建必要的目录
RUN mkdir -p uploads output temp

# 暴露端口（如果需要运行Gradio应用）
EXPOSE 7860