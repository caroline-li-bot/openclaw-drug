# 公开可获取的生物医药文献与数据集资源

这份文档整理了可以公开获取的生物医药文献、化合物、靶标、疾病相关数据集，可用于 DrugClaw 检索和 RAG。

## 📚 文献资源

### 开放获取文献
- **PubMed Central (PMC)** - 数百万开放获取的生物医学论文全文
  - https://www.ncbi.nlm.nih.gov/pmc/
  - API 访问：https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
  - 可以批量下载全文 PDF/XML

- **arXiv** - 预印本，包含大量计算生物学/药物发现论文
  - https://arxiv.org/list/q-bio/
  - API: https://arxiv.org/help/api

- **bioRxiv** - 生物学预印本服务器
  - https://www.biorxiv.org/
  - 专注于生物学预印本，很多药物发现最新研究

- **medRxiv** - 医学预印本
  - https://www.medrxiv.org/

- **ScienceDirect open access** - 爱思唯尔开放获取文献
  - https://www.sciencedirect.com/open-access

- **Directory of Open Access Journals (DOAJ)**
  - https://doaj.org/
  - 开放获取期刊目录

### 全文挖掘数据集
- **Allen AI CORD-19** - COVID-19 开放学术数据集
  - https://www.kaggle.com/datasets/allen-institute-for-ai/CORD-19-research-challenge
  - 包含 ~500k 论文全文，可用于 RAG 测试
  
- **PubMed Central Open Access Subset**
  - https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/
  - ~400k 开放获取论文，可以批量下载

- **Semantic Scholar Open Research Corpus**
  - https://www.semanticscholar.org/product/api
  - 大规模学术文献 API，免费用于研究

## 🧪 化合物与药物数据集

### 药物靶标相互作用
- **ChEMBL** - 手动整理的生物活性分子数据库
  - https://www.ebi.ac.uk/chembl/
  - 公开下载：https://ftp.ebi.ac.uk/pub/databases/chembl/
  - 包含 ~2M 化合物， ~15M 生物活性数据

- **BindingDB** - 公开的药物-靶标结合亲和力数据库
  - https://www.bindingdb.org/bind/index.jsp
  - ~1M 化合物-蛋白结合数据

- **DrugBank** - 综合药物信息数据库
  - https://go.drugbank.com/
  - 需要注册免费下载，包含 ~14k 药物， ~5k 靶标

- **Therapeutic Target Database (TTD)**
  - http://db.idrblab.net/ttd/
  - ~3k 已知治疗靶标， ~2k 药物

- **DGIdb** - Drug-Gene Interaction database
  - https://dgidb.org/
  - 整理了已知的药物-基因相互作用

### 化合物库
- **ZINC** - 免费可购买化合物库，用于虚拟筛选
  - https://zinc.docking.org/
  - 数十亿化合物，可以下载子集

- **Enamine Docking Library**
  - https://enamine.net/library-synthesis/real-compound-libraries
  - 数百万可购买化合物

- **PubChem** - 开放式化合物数据库
  - https://pubchem.ncbi.nlm.nih.gov/
  - ~100M 化合物，可下载 SDF 格式

- **ChEMBL Ready-to-Dock Datasets**
  - https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/

### ADMET 与毒性数据集
- **LiverTox** - 药物肝毒性数据库
  - https://livertox.nlm.nih.gov/
  - 可以下载结构化数据

- **SIDER** - 药物副作用和不良反应
  - http://sideeffects.embl.de/
  - ~1k 药物， ~14k 副作用

- **FAERS** - FDA 不良事件报告系统
  - https://open.fda.gov/data/faers/
  - 数百万不良事件报告，可以公开下载

- **DILIrank** - 药物性肝损伤数据集
  - https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/dilirank

- **UniTox** - 统一化合物毒性数据库
  - https://unitox.net/

### 药物不良反应
- **MedLinePlus** - NIH 药物信息
  - https://medlineplus.gov/druginfo.html
  - 公开 API 访问

- **DailyMed** - FDA 药品标签
  - https://dailymed.nlm.nih.gov/dailymed/
  - 可以下载全部药品标签文本

- **openFDA** - 开放药品数据
  - https://open.fda.gov/
  - 药品标签、不良事件、召回

### 药物-药物相互作用
- **DDInter** - Drug-Drug Interaction Database
  - https://ddinter.scbdd.com/
  - ~2k 药物， ~36k 相互作用

- **DrugBank Drug Interactions** - 包含在 DrugBank 中

### 药物重定位
- **RepoDB** - 标准药物重定位数据集
  - https://repodb.net/
  - 已上市药物的重定位数据

- **DRKG** - Drug Repurposing Knowledge Graph
  - https://github.com/gnn4dr/DRKG
  - 知识图谱，包含药物、疾病、基因

- **Drug Repurposing Hub**
  - https://clue.io/repurposing
  - Broad Institute 整理

### 药物基因组学
- **PharmGKB** - Pharmacogenomics Knowledgebase
  - https://www.pharmgkb.org/
  - 药物基因组学数据，基因型-药物反应

- **CPIC** - Clinical Pharmacogenetics Implementation Consortium
  - https://cpicpgx.org/
  - 临床药物基因组学指南

## 🔬 靶标与疾病数据集

- **UniProt** - 蛋白质序列和功能信息
  - https://www.uniprot.org/
  - 完整下载，批量访问

- **PDB** - Protein Data Bank，蛋白质结构
  - https://www.rcsb.org/
  - ~180k 蛋白质结构，可下载

- **AlphaFold DB** - 预测蛋白质结构
  - https://alphafold.ebi.ac.uk/
  - 几乎所有人类蛋白的预测结构，可批量下载

- **ClinVar** - 临床变异数据库
  - https://www.ncbi.nlm.nih.gov/clinvar/
  - 变异与疾病关联

- **Open Targets** - 靶标治疗相关性
  - https://www.targetvalidation.org/
  - 整合基因组相关性数据给靶标打分

- **STRING** - 蛋白质-蛋白质相互作用
  - https://string-db.org/
  - 可以下载整个相互作用网络

- **Reactome** - 信号通路数据库
  - https://reactome.org/
  - 生物学通路注释

## 🗺️ 本体与标准化

- **RxNorm** - 标准化药品名称
  - https://www.nlm.nih.gov/research/umls/rxnorm/
  - API 访问，下载
  
- **ChEBI** - Chemical Entities of Biological Interest
  - https://www.ebi.ac.uk/chebi/
  - 化学品本体

- **ATC/DDD** - WHO Anatomical Therapeutic Chemical Classification
  - https://www.who.int/tools/atc-ddd-toolkit

## 🧬 组学数据集

- **GEO** - Gene Expression Omnibus
  - https://www.ncbi.nlm.nih.gov/geo/
  - 基因表达谱数据，公开下载

- **TCGA** - The Cancer Genome Atlas
  - https://portal.gdc.cancer.gov/
  - 肿瘤多组学数据，公开下载

- **GTEx** - Genotype-Tissue Expression
  - https://gtexportal.org/home/
  - 正常组织表达数据

## 📊 可直接用于 RAG 的开源知识库

### 预处理好的数据集
- **MedQA** - 医学问答数据集
  - https://github.com/jindwang/MedQA
  - 可以用于训练/测试
  
- **PubMedQA** - 生物医学问答
  - https://pubmedqa.github.io/

- **BioASQ** - 生物医学语义问答挑战
  - http://bioasq.org/

### 开放知识图谱
- **Hetionet** - 异质性生物医学知识图谱
  - https://github.com/dhimmel/hetionet
  - 包含药物、疾病、基因相互作用

- **DRKG** - Drug Repurposing Knowledge Graph (上面已列)

## 🔗 GitHub 上的整理资源

- **awesome-biomedical-ai**
  https://github.com/kexinhuang12345/awesome-biomedical-ai

- **awesome-bioinformatics**
  https://github.com/danielecook/awesome-bioinformatics

- **awesome-cheminformatics**
  https://github.com/hsiaoyc0909/awesome-cheminformatics

- **awesome-drug-discovery**
  https://github.com/OCRLab/awesome-drug-discovery

- **opensource-drug-discovery**
  https://github.com/volkamerlab/awesome-opensource-drug-discovery

## 💾 数据下载技巧

1. **对于大型数据库**：下载子集用于测试，全量数据存在云端或本地存储
2. **API 访问优先**：大多数数据库提供 API，不需要全量下载
3. **看 license**：有些资源非商用免费，注意版权

## 🎯 DrugClaw RAG 使用建议

1. **私有文献**：上传你自己收集的 PDF，建立私人文献知识库
2. **公共文献**：使用上述公开资源，批量导入 RAG
3. **混合检索**：同时检索公共数据库和私人文献，给出综合回答
