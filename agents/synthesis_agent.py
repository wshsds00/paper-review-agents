from utils.llm_client import call_llm

PLAN_PROMPT = """根据下面的多篇论文对比分析，请为一篇学术综述生成大纲，要求包含：
- 领域背景与现状
- 各方法详细介绍与优劣比较
- 未来可能的研究方向

请用Markdown标题层级（## 表示大标题）列出大纲，每个要点一行。

对比分析内容：
{comparison_result}
"""

WRITING_PROMPT = """请根据以下大纲和对比细节，撰写一篇完整的综述草稿。要求：
- 语言学术化，逻辑严密
- 正文中引用论文时使用序号[1][2]...
- 对每个方法都要说明其核心创新点和不足
- 每个章节的内容要详细，不要只是标题

大纲：
{outline}

对比细节：
{comparison_detail}
"""

def generate_outline(comparison_text: str) -> str:
    messages = [{"role": "user", "content": PLAN_PROMPT.format(comparison_result=comparison_text)}]
    return call_llm(messages)

def write_section_by_section(outline: str, comparison_detail: str) -> str:
    messages = [{"role": "user", "content": WRITING_PROMPT.format(outline=outline,
                                                                  comparison_detail=comparison_detail)}]
    return call_llm(messages)