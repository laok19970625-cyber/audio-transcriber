"""命令行入口：语音转写 + 会议纪要。

用法：
  python main.py transcribe <音频文件>   # 转写音频
  python main.py summarize <文本文件>    # 从文本生成纪要
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio_summary import LLMClient, summarize, transcribe  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("  python main.py transcribe <音频文件>")
        print("  python main.py summarize <文本文件>")
        return

    cmd, path = sys.argv[1], sys.argv[2]
    try:
        if cmd == "transcribe":
            text = transcribe(path)
            print("=== 转写结果 ===")
            print(text)
            print("\n=== 会议纪要 ===")
            print(summarize(text, LLMClient()))
        elif cmd == "summarize":
            text = Path(path).read_text(encoding="utf-8")
            print("=== 会议纪要 ===")
            print(summarize(text, LLMClient()))
        else:
            print(f"未知命令：{cmd}")
    except RuntimeError as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    main()
