"""语音转文字 + 会议纪要摘要。

录音转写依赖语音识别 API。本实现提供：
1. transcribe()：调用智谱/OpenAI 兼容的语音转写接口（Whisper 类）。
2. summarize()：把转写文本交给 LLM 生成结构化会议纪要。

若语音 API 不可用，可先用 .txt 文本直接走摘要流程（transcribe 留好接口位）。
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from pathlib import Path


class LLMClient:
    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.api_base = (api_base or os.environ.get("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")).rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL", "glm-4-flash")

    def chat(self, messages, temperature=0.3):
        if not self.api_key:
            raise RuntimeError("未配置 LLM_API_KEY，请设置环境变量后重试。")
        url = f"{self.api_base}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


def transcribe(audio_path: str, api_base: str | None = None) -> str:
    """调用 OpenAI 兼容的 /audio/transcriptions 接口转写音频。

    需要目标服务支持 audio/transcriptions（如 OpenAI、部分兼容服务）。
    若服务不支持，请改用各自 SDK。此函数提供标准实现。
    """
    api_key = os.environ.get("LLM_API_KEY", "")
    base = (api_base or os.environ.get("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")).rstrip("/")
    if not api_key:
        raise RuntimeError("未配置 LLM_API_KEY")

    boundary = "----wb-boundary"
    audio_bytes = Path(audio_path).read_bytes()
    # 简单 multipart 构造
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="audio.mp3"\r\n'
        "Content-Type: audio/mpeg\r\n\r\n"
    ).encode() + audio_bytes + (
        f"\r\n--{boundary}\r\n"
        'Content-Disposition: form-data; name="model"\r\n\r\n'
        "whisper-1\r\n"
        f"--{boundary}--\r\n"
    ).encode()

    req = urllib.request.Request(
        f"{base}/audio/transcriptions",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8")).get("text", "")


SUMMARY_PROMPT = (
    "请把下面的会议录音转写文本整理成结构化会议纪要，包含：\n"
    "1) 会议主题 2) 关键结论 3) 待办事项（含负责人） 4) 重要时间节点。\n"
    "用中文，简洁清晰。如果文本内容较少，就提取能提取的信息。"
)


def summarize(transcript: str, llm: LLMClient | None = None) -> str:
    llm = llm or LLMClient()
    messages = [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": transcript},
    ]
    return llm.chat(messages)
