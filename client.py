from openai import OpenAI

# 初始化客户端并连接到本地服务器
client = OpenAI(
    api_key="fake-api-key",
    base_url="http://localhost:8000/v1"  # 如果需要更改默认端口，可以在这里修改
)

# 多轮对话
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }

    ],
    stream=True,
    model="vivo-BlueLM-TB-Pro",
)
for i in chat_completion:
    print(i.choices[0].delta.content or "")


# 非流式调用，单论对话
chat_completion = client.completions.create(
    prompt="Say this is a test",
    model="vivo-BlueLM-TB-Pro",
)
print(chat_completion.choices[0].message)
