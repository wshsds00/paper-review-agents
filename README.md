\# PaperReview Agents — 多Agent协作论文综述生成器



一个基于多 Agent 协作与长链推理的学术论文自动精读及综述生成工具，旨在解决学生阅读多篇顶会论文并撰写综述时耗时且易遗漏矛盾的痛点。



\## 系统架构



\- \*\*Agent 1 – 翻译抽取 Agent\*\*：从论文（摘要或全文）提取背景、方法、实验、局限四要素

\- \*\*Agent 2 – 对比分析 Agent\*\*：横向对比多篇论文，输出异同、共有缺陷和互补方向

\- \*\*Agent 3 – 综述撰写 Agent（长链推理）\*\*：先规划综述大纲，再逐节扩写，自动插入引用序号，输出完整 Markdown 草稿



整个流水线串行协作，人工仅需最终复核与润色。



\## 快速开始



\### 安装依赖  
pip install -r requirements.txt

\### 配置 API Key
\### 安装依赖  复制环境变量模板
cp .env.example .env
\### 安装依赖  编辑 .env，将 sk-your-api-key-here 替换为你的真实 API Key（OpenAI 或兼容接口）

