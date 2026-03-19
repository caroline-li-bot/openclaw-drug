# DrugClaw - OpenClaw 药物研发自动化助手

💊 基于 OpenClaw 的全栈药物发现自动化助手，加速从文献分析到实验设计的完整药物研发流程。

[English Version](/README.md) | [在线演示](https://drug.openclaw.ai)

DrugClaw 是 OpenClaw 原生的药物研发自动化助手，结合了领域技能、工具调用和智能自动化，帮助研究人员更快地完成工作。

## 🎯 核心功能

DrugClaw 覆盖完整的药物发现流水线：

### 🔍 文献与知识
- **文献分析** - 自动 PubMed 搜索，关键信息提取，研究趋势分析
- **靶标情报** - 整合 UniProt、OpenTargets、Reactome、STRING、ClinVar 构建靶标档案
- **证据合成** - 从多个数据库聚合证据，推导出有理有据的结论

### 🧪 化合物筛选与预测
- **虚拟筛选** - 自动化 AutoDock Vina 分子对接，后处理和排名
- **ADMET 预测** - 使用 ChemBERTa 进行启发式 ADMET 性质预测
- **药物-靶标相互作用 (DTI)** - 查询 ChEMBL、BindingDB、DGIdb、TTD 已知相互作用
- **分子生成** - 基于骨架约束生成新型分子

### 📊 数据分析与实验设计
- **实验方案设计** - 自动生成细胞/动物实验方案
- **统计分析** - 自动化数据处理、可视化和统计检验
- **临床试验设计** - 方案设计辅助，入组标准选择

### 🔬 领域专项技能
- **药物不良反应 (ADR)** - 查询 FAERS、SIDER、nSIDES 药物不良反应
- **药物相互作用 (DDI)** - 从多个数据源检查相互作用
- **药物基因组学 (PGx)** - 查询 PharmGKB 基因型指导用药
- **药物重定位** - 从 RepoDB、DRKG 识别重定位机会
- 等等...

## 🤖 智能工作流

DrugClaw 借鉴了 [QSong-github/DrugClaw](https://github.com/QSong-github/DrugClaw) 的检索-执行智能体模式：

```
用户查询 → 规划智能体 → 技能选择 → 代码智能体 → 检索 → 推理 → 报告
```

1. **规划智能体** - 分析查询，识别实体，选择相关技能
2. **代码智能体** - 阅读技能文档，编写并执行特定数据源的查询代码
3. **回退机制** - 如果代码生成失败，自动回退到预编写的确定性检索脚本
4. **推理合成** - 聚合多个来源的证据，生成结构化报告

## 🗺️ 技能树 (15 个分类)

| 分类 | 描述 | 数据源 |
|------|------|--------|
| **dti** | 药物-靶标相互作用 | ChEMBL, BindingDB, DGIdb, OpenTargets, TTD, STITCH |
| **adr** | 药物不良反应 | FAERS, SIDER, nSIDES, ADReCS |
| **ddi** | 药物-药物相互作用 | MecDDI, DDInter, KEGG Drug |
| **pgx** | 药物基因组学 | PharmGKB, CPIC |
| **repurposing** | 药物重定位 | RepoDB, DRKG, OREGANO, Drug Repurposing Hub |
| **knowledgebase** | 药物知识库 | DrugBank, UniD3, IUPHAR/BPS, DrugCentral, WHO 基本药物目录 |
| **mechanism** | 作用机制 | DRUGMECHDB |
| **labeling** | 药品说明书 | DailyMed, openFDA, MedlinePlus |
| **toxicity** | 药物毒性 | UniTox, LiverTox, DILIrank |
| **ontology** | 本体与标准化 | RxNorm, ChEBI, ATC/DDD |
| **combination** | 药物组合 | DrugCombDB, DrugComb |
| **properties** | 分子性质 | GDSC, ChemBERTa |
| **disease** | 药物-疾病关联 | SemaTyP |
| **reviews** | 患者评价 | WebMD, Drugs.com |
| **nlp** | NLP 数据集 | DDI Corpus, DrugProt, ADE Corpus, CADEC |

## 🛠️ 技术栈

- **OpenClaw** - 智能体框架，技能系统，记忆，多通道支持
- **RDKit** - 化学信息学
- **ChemBERTa-2** - 分子性质预测
- **ESMFold** - 蛋白质结构预测
- **DiffDock** - 分子对接
- **AutoDock Vina** - 虚拟筛选
- **LangChain** - RAG 和智能体编排
- **Supabase** - 云数据库（可选）
- **Flask** - Web 界面

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/caroline-li-bot/DrugClaw.git
cd DrugClaw

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 作为 OpenClaw 技能安装
openclaw skill install .
```

更多部署选项见 [DEPLOYMENT.md](/DEPLOYMENT.md)。

## 🚀 快速开始

### 作为 OpenClaw 技能使用

```python
# 在 OpenClaw 聊天中直接自然提问：
# "查找 imatinib 所有已知靶标并总结潜在的不良相互作用"
# "从 ZINC 库中筛选潜在的 EGFR 抑制剂"
# "预测这个 SMILES 的 ADMET 性质：CC1=CC=C(C=C1)N... "
```

### 命令行接口

```bash
# 文献分析
drugclaw literature analyze --keyword "EGFR inhibitor" --output report.md

# 虚拟筛选
drugclaw screening run --target PDB:1M17 --library zinc15 --output candidates.csv

# ADMET 预测
drugclaw admet predict --smiles "C1=CC(=C(C=C1Cl)Cl)O" --output properties.csv

# 实验方案设计
drugclaw experiment design --type "cell viability" --compound "Gefitinib" --output protocol.md
```

## ☁️ Web 部署

DrugClaw 可以部署到 Vercel 使用 Supabase 后端。详见 [DEPLOYMENT_VERCEL_SUPABASE.md](/DEPLOYMENT_VERCEL_SUPABASE.md)。

## 📁 项目结构

```
DrugClaw/
├── drugclaw/                    # 主包
│   ├── __init__.py
│   ├── agent/                   # 智能体架构
│   │   ├── planner.py           # 查询规划智能体
│   │   ├── code_agent.py        # 代码生成智能体
│   │   └── responder.py         # 最终答案合成
│   ├── cli.py                   # 命令行接口
│   ├── config.py                # 配置处理
│   └── main_system.py           # 主入口
├── skills/                      # 技能树（15个分类）
│   ├── dti/                     # 药物-靶标相互作用
│   │   └── */                   # 每个数据源: SKILL.md, example.py, retrieve.py
│   ├── adr/                     # 药物不良反应
│   ├── ddi/                     # 药物-药物相互作用
│   ├── pgx/                     # 药物基因组学
│   ├── repurposing/             # 药物重定位
│   ├── knowledgebase/           # 药物知识库
│   ├── mechanism/               # 作用机制
│   ├── labeling/                # 药品说明书
│   ├── toxicity/                # 药物毒性
│   ├── ontology/                # 本体与标准化
│   ├── combination/             # 药物组合
│   ├── properties/              # 分子性质
│   ├── disease/                 # 药物-疾病关联
│   ├── reviews/                 # 患者评价
│   └── nlp/                     # NLP 数据集
├── utils/                       # 工具库
│   ├── chem_utils.py            # 化学信息学工具
│   ├── db_utils.py              # 数据库工具
│   ├── ml_utils.py              # 机器学习模型
│   ├── sota_models.py           # SOTA 模型 (ChemBERTa, ESMFold, DiffDock)
│   └── supabase_utils.py        # Supabase 集成（可选）
├── web/                         # Web 界面
│   ├── app.py                   # Flask 后端
│   ├── templates/               # HTML 模板
│   └── static/                  # CSS/JS 资源
├── supabase/                    # Supabase 配置
│   └── migrations/              # 数据库迁移
├── examples/                    # 示例使用脚本
├── docs/                        # 文档
├── requirements.txt             # Python 依赖
├── skill.yaml                   # OpenClaw 技能清单
└── README.md                    # 本文件
```

## 🎯 与其他 DrugClaw 项目的区别

| 方面 | DrugClaw/DrugClaw | QSong-github/DrugClaw | **本项目 DrugClaw** |
|------|-------------------|------------------------|---------------------|
| **基础** | Rust 智能体运行时 | LangGraph Agentic RAG | **OpenClaw 原生技能** |
| **范围** | 完整研究工作流自动化 | 药物知识问答 | **全栈药物发现自动化 + Agentic RAG** |
| **理念** | 带药物技能的通用智能体 | 专门用于药物问题的 RAG | **结合两者优势：OpenClaw 智能体 + 15分类技能树 + 智能工作流** |

## 📄 许可证

MIT License - 详见 [LICENSE](/LICENSE)。

## 🙏 致谢

- 灵感来自 [DrugClaw/DrugClaw](https://github.com/DrugClaw/DrugClaw) 和 [QSong-github/DrugClaw](https://github.com/QSong-github/DrugClaw)
- 基于 [OpenClaw](https://github.com/openclaw/openclaw) 智能体框架构建
- 使用了公开可用的生物医学数据库和开源工具

---

*DrugClaw 仅用于研究目的。不提供医疗建议。所有预测都需要实验验证。*
