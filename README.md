#  Vivo AI OpenAI-Like API

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

**将 蓝心大模型 接口封装成 OpenAI 兼容格式。**


## 特性

* **兼容 OpenAI Chat Completions API:** 实现了 `/v1/chat/completions`和`/v1/completions` 接口，支持非流式和流式响应。



### 配置

在 `main.py` 文件中填写你的 vivo AI 平台的 App ID 和 App Key：
    
```python
    gpt = VivoGPT(app_id="", app_key="")
   ```

