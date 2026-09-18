import re
from utils.llm_client import call_llm

PLAN_PROMPT = """根据下面的多篇论文对比分析，请为一篇学术综述生成大纲，要求包含：
- 领域背景与现状
- 各方法详细介绍与优劣比较
- 未来可能的研究方向

请用Markdown标题层级（## 表示大标题）列出大纲，每个要点一行。

对比分析内容：
{comparison_result}
"""

# 逐节撰写：每次只写一个小节，带上全局大纲和前文上下文
SECTION_PROMPT = """你正在撰写一篇学术综述的其中一个小节。

## 完整大纲
{outline}

## 当前要写的小节
标题：{title}

## 对比分析细节
{comparison_detail}

## 前面已写章节的摘要（用于保持连贯，避免重复）
{previous_context}

## 写作要求
1. 语言学术化，逻辑严密
2. 引用编号规则：第 1 篇论文在全文中固定用 [1]，第 2 篇固定用 [2]，以此类推，各节必须沿用同一套编号，不要重新编号
3. 说明每个方法的创新点与不足
4. 内容要充实详细，不要只写小标题，至少 300 字
5. 不要与前面章节的内容重复
6. 直接输出正文内容，不要重复输出小节标题

请开始撰写：
"""

# 一致性检查：全文拼接后做一次终检
CONSISTENCY_PROMPT = """请对以下综述全文做一致性检查，直接输出修正后的完整全文（Markdown 格式）。

检查要点：
1. 各小节之间是否有明显重复内容，如有请合并或删减
2. 引用编号 [1][2][3] 是否连续、一致，有没有跳号或各节编号不统一
3. 前后是否有矛盾的说法
4. 修正后直接输出全文，不要输出检查报告

原文：
{full_text}
"""

# 默认小节标题（大纲解析失败时降级使用）
DEFAULT_SECTIONS = ["研究背景与现状", "各方法详细介绍与优劣比较", "未来可能的研究方向"]

# 占位文本常量：生成失败时使用，一致性检查会跳过以保留此标记
PLACEHOLDER_TEXT = "（本节生成失败，请人工补写）"


def generate_outline(comparison_text: str) -> str:
    """调用 LLM 生成综述大纲。"""
    messages = [{"role": "user", "content": PLAN_PROMPT.format(comparison_result=comparison_text)}]
    return call_llm(messages)


def parse_outline(outline: str) -> list[str]:
    """把 LLM 生成的大纲文本解析成小节标题列表。"""
    sections: list[str] = []
    for line in outline.strip().splitlines():
        line = line.strip()
        # 跳过空行和分隔线
        if not line or re.match(r'^-{3,}$', line):
            continue
        # Markdown 标题：## xxx
        m = re.match(r'^#{1,6}\s+(.+)$', line)
        if m:
            sections.append(m.group(1).strip())
            continue
        # 无序列表：- xxx 或 * xxx
        m = re.match(r'^[-*]\s+(.+)$', line)
        if m:
            sections.append(m.group(1).strip())
            continue
        # 有序列表：1. xxx 或 1、xxx
        m = re.match(r'^\d+[.、)\]]\s*(.+)$', line)
        if m:
            sections.append(m.group(1).strip())
            continue
        # 加粗标题：**xxx**
        m = re.match(r'^\*\*(.+?)\*\*\s*$', line)
        if m:
            sections.append(m.group(1).strip())
            continue

    # 过滤掉过短的条目
    sections = [s for s in sections if len(s) >= 2]

    # 健壮性：少于 2 个小节时降级
    if len(sections) < 2:
        print("  大纲解析结果不足，使用默认章节结构")
        return DEFAULT_SECTIONS

    print(f"  已解析出 {len(sections)} 个小节")
    return sections


def write_section_by_section(outline: str, comparison_detail: str) -> str:
    """逐节调用 LLM 撰写综述，最后做一致性检查，返回完整 Markdown 全文。"""
    sections = parse_outline(outline)
    n = len(sections)
    written: list[tuple[str, str]] = []  # (标题, 正文)
    failed_sections: list[str] = []      # 记录生成失败的小节标题

    # 逐节撰写
    for i, title in enumerate(sections, 1):
        print(f"  正在撰写第 {i}/{n} 节：{title}")

        # 构造前文上下文：每节取标题 + 正文前 200 字
        if written:
            previous_parts = []
            for t, b in written:
                snippet = b[:200].rstrip()
                previous_parts.append(f"### {t}\n{snippet}...")
            previous_context = "\n\n".join(previous_parts)
        else:
            previous_context = "（暂无，这是第一节）"

        prompt = SECTION_PROMPT.format(
            outline=outline,
            title=title,
            comparison_detail=comparison_detail,
            previous_context=previous_context,
        )
        messages = [{"role": "user", "content": prompt}]

        # 容错：调用失败或返回空则用占位文本
        try:
            body = call_llm(messages)
            if not body or not body.strip():
                print(f"    ⚠ 第 {i} 节生成结果为空，使用占位文本")
                body = PLACEHOLDER_TEXT
                failed_sections.append(title)
        except Exception as e:
            print(f"    ⚠ 第 {i} 节生成异常：{e}，使用占位文本")
            body = PLACEHOLDER_TEXT
            failed_sections.append(title)

        written.append((title, body.strip()))

    # 拼接全文
    full_text = "\n\n".join(f"## {t}\n\n{b}" for t, b in written)

    # 有失败小节时跳过一致性检查，避免占位标记被覆盖
    if failed_sections:
        titles = "、".join(failed_sections)
        print(f"  ⚠ 有 {len(failed_sections)} 个小节生成失败：{titles}，跳过一致性检查以避免失败标记被覆盖")
        print("  （提示：请人工补写上述小节，或直接编辑输出文件）")
        return full_text

    # 一致性检查
    print("  正在进行全文一致性检查...")
    try:
        check_prompt = CONSISTENCY_PROMPT.format(full_text=full_text)
        messages = [{"role": "user", "content": check_prompt}]
        result = call_llm(messages)
        if result and result.strip():
            full_text = result.strip()
        else:
            print("    ⚠ 一致性检查返回空，使用拼接原文")
    except Exception as e:
        print(f"    ⚠ 一致性检查失败：{e}，使用拼接原文")

    return full_text
