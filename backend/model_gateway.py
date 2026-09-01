from typing import Dict

# 模拟模型调用（真实项目里可以接 OpenAI / Azure / 本地模型）
def call_model(prompt: str, context: Dict | None = None) -> str:
    """
    Model Gateway:
    - 接收 prompt + context
    - 统一管理模型调用
    - 未来可以加日志、限流、fallback
    """
    # 这里用简单规则模拟
    if "study plan" in prompt.lower():
        return "Weekly Study Plan: 1) Review notes 2) Practice problems 3) Take a quiz."
    return "Model response placeholder."
