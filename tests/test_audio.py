"""音频转写+摘要单元测试（摘要部分不依赖真实 API）。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio_summary import LLMClient, summarize  # noqa: E402


class FakeLLM(LLMClient):
    def chat(self, messages, temperature=0.3):
        return "[纪要] " + messages[-1]["content"][:30]


class TestSummarize(unittest.TestCase):
    def test_summarize(self):
        transcript = "今天讨论了下季度目标，张三负责市场，李四负责技术，下周五前提交方案。"
        result = summarize(transcript, FakeLLM())
        self.assertIn("[纪要]", result)

    def test_summarize_empty(self):
        result = summarize("", FakeLLM())
        self.assertIn("[纪要]", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
