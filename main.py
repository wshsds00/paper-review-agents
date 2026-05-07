import sys
import os
from utils.pdf_parser import extract_text_from_pdf
from agents.extract_agent import extract_paper_info
from agents.compare_agent import compare_papers
from agents.synthesis_agent import generate_outline, write_section_by_section

DEMO_PAPERS = [
    {
        "title": "Improving Image Classification via Attention-Augmented CNNs",
        "abstract": "We propose an attention mechanism that enhances CNN feature maps for image classification. "
                    "Experiments on ImageNet show 2.3% top-1 accuracy improvement over ResNet-50 baseline. "
                    "However, the increased computation cost may limit deployment on resource-constrained devices."
    },
    {
        "title": "Vision Transformers for Large-Scale Image Recognition",
        "abstract": "We apply a pure Transformer architecture directly to sequences of image patches for classification. "
                    "Our model achieves state-of-the-art on multiple benchmarks when pre-trained on large datasets. "
                    "It requires substantial data and compute, and lacks the inductive biases of CNNs."
    },
    {
        "title": "Efficient Hybrid Models: Combining CNNs and Transformers",
        "abstract": "We introduce a hybrid architecture that uses CNN for local feature extraction and Transformer "
                    "for global context modeling. The model achieves competitive accuracy with fewer parameters than "
                    "pure transformers, but the design of interaction layers needs further exploration."
    }
]

def run_pipeline(pdf_paths=None):
    if pdf_paths is None:
        print(">>> DEMO 模式：使用内置论文摘要")
        extracted = []
        for paper in DEMO_PAPERS:
            text = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
            print(f"正在提取：{paper['title']}")
            info = extract_paper_info(text)
            extracted.append(info)
    else:
        print(f">>> PDF 模式：共 {len(pdf_paths)} 篇论文")
        extracted = []
        for path in pdf_paths:
            print(f"正在解析：{path}")
            full_text = extract_text_from_pdf(path)
            truncated = full_text[:3000]
            print(f"截取前3000字符进行提取...")
            info = extract_paper_info(truncated)
            extracted.append(info)

    print("\n>>> 正在进行论文横向对比分析...")
    comparison = compare_papers(extracted)
    print("对比分析完成\n")

    print(">>> 正在生成综述大纲...")
    outline = generate_outline(comparison)
    print("大纲已生成，开始撰写全文...\n")
    review = write_section_by_section(outline, comparison)

    os.makedirs("output", exist_ok=True)
    output_path = "output/review_draft.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 自动生成综述草稿\n\n{review}")
    print(f" 综述已保存至 {output_path}")
    return review

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_pipeline(pdf_paths=None)
    elif len(sys.argv) > 1:
        run_pipeline(pdf_paths=sys.argv[1:])
    else:
        print("使用方法：")
        print("  Demo 模式：python main.py --demo")
        print("  PDF 模式：python main.py paper1.pdf paper2.pdf ...")
