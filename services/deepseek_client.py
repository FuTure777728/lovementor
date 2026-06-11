"""
DeepSeek API 统一调用封装
"""
import json
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class DeepSeekClient:
    """DeepSeek Chat API 客户端"""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.model = DEEPSEEK_MODEL

    def chat(self, user_message: str, system_prompt: str = "",
             temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        调用 DeepSeek Chat API

        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            temperature: 温度参数 (0-2)
            max_tokens: 最大 token 数

        Returns:
            API 返回的文本内容
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise DeepSeekError("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise DeepSeekError(f"API 请求失败: {str(e)}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise DeepSeekError(f"API 返回格式异常: {str(e)}")

    def chat_json(self, user_message: str, system_prompt: str = "",
                  temperature: float = 0.3) -> dict:
        """
        调用 API 并期望返回 JSON 格式结果

        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            temperature: 温度参数

        Returns:
            解析后的 JSON 字典
        """
        full_system = system_prompt
        full_system += "\n\n【重要】请严格只输出 JSON 格式，不要包含任何 markdown 代码块标记，不要有任何额外解释文字。"

        raw_response = self.chat(
            user_message=user_message,
            system_prompt=full_system,
            temperature=temperature
        )

        # 清理可能的 markdown 代码块
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # 去掉第一行 ```json 和最后一行 ```
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取 JSON 对象
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            raise DeepSeekError("无法解析 API 返回的 JSON 格式")


class DeepSeekError(Exception):
    """DeepSeek API 错误"""
    pass


# 全局单例
_client = None


def get_client() -> DeepSeekClient:
    """获取 DeepSeek API 客户端单例"""
    global _client
    if _client is None:
        _client = DeepSeekClient()
    return _client
