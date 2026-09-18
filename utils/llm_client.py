import openai
import os
from dotenv import load_dotenv

load_dotenv()

# 默认模型，可通过环境变量 OPENAI_MODEL 覆盖（使用第三方/兼容接口时通常需要换成本平台支持的模型名）
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# base_url 留空时使用 OpenAI 官方地址；使用 OpenAI 兼容接口时通过 OPENAI_BASE_URL 指定
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)


def call_llm(messages, model=None, temperature=0.3):
    """调用大模型。model 传 None 时使用 DEFAULT_MODEL。"""
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content