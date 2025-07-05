#  Vivo AI OpenAI-Like API

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

**将 蓝心大模型 接口封装成 OpenAI 兼容格式。**


## 特性

* **兼容 OpenAI Chat Completions API:** 实现了 `/v1/chat/completions`和`/v1/completions` 接口，支持非流式和流式响应。

## 配置

在 `.env` 文件中填写你的 vivo AI 平台的 App ID 和 App Key：

```shell
cp .env.example .env
```

编辑 `.env` 文件：

```
VIVO_APP_ID=YOUR_APP_ID
VIVO_APP_KEY=YOUR_APP_KEY
```

## 运行方式

### 方式一：本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 直接运行：
```bash
python main.py
```

服务将在 http://localhost:8000 启动

### 方式二：Docker 运行

1. 使用 Docker Compose 构建并启动（推荐）：
```bash
docker compose up -d --build
```

2. 查看日志：
```bash
docker compose logs -f
```

3. 停止服务：
```bash
docker compose down
```

### API 使用

服务启动后，可以通过以下端点访问：

- Chat Completions: `POST /v1/chat/completions`
- Completions: `POST /v1/completions`
- API 文档: http://localhost:8000/docs

