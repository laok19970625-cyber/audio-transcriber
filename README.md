# 语音转文字 + 会议纪要

把会议录音转写为文字，并自动生成结构化会议纪要（主题、结论、待办、时间节点）。

## 特性
- `transcribe`：调用 OpenAI 兼容的 audio/transcriptions 接口
- `summarize`：LLM 生成结构化会议纪要
- 也可跳过转写，直接对文本生成纪要

## 快速开始
```bash
export LLM_API_KEY="你的Key"
python main.py transcribe meeting.mp3   # 转写+纪要
python main.py summarize meeting.txt    # 纯文本纪要
```

## 应用场景
- 会议纪要自动化
- 访谈/播客内容整理
- 录音归档

## License
MIT
