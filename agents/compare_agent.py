from utils.llm_client import call_llm

COMPARE_PROMPT = """下面是多篇论文的结构化信息。请对这些论文进行横向对比分析，包含：
1. 各篇论文方法的异同点（可用表格）
2. 共同存在的缺陷或局限性
3. 哪些方法可以互补，给出可能的融合方向

请用中文输出。

论文信息：
{combined_info}
"""

def compare_papers(extracted_infos: list) -> str:
    combined = "\n\n".join([f"论文{i+1}：{info}" for i, info in enumerate(extracted_infos)])
    messages = [{"role": "user", "content": COMPARE_PROMPT.format(combined_info=combined)}]
    return call_llm(messages)