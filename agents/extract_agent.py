from utils.llm_client import call_llm

EXTRACTION_PROMPT = """你是一位顶会论文评审。请阅读以下论文内容（可能是全文或摘要），提取四要素，并严格按照JSON格式输出，不要输出其他内容：
{{
  "background": "研究背景与问题",
  "method": "提出的方法或模型",
  "experiments": "关键实验与结果",
  "limitations": "方法局限或未来工作"
}}

论文内容：
{paper_text}
"""

def extract_paper_info(paper_text: str) -> str:
    messages = [{"role": "user", "content": EXTRACTION_PROMPT.format(paper_text=paper_text)}]
    return call_llm(messages)