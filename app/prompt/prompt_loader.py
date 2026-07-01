from pathlib import Path


def load_prompt(name: str) -> str:
    # 根据指定的名称拼接提示词所在的路径
    prompt_path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"
    # 可以使用Path中的函数直接读取即可
    return prompt_path.read_text(encoding="utf-8")
