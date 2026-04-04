# RAG (Retrieval-Augmented Generation) Skill

> GO2SE 知识增强检索系统

## 功能定位

RAG为GO2SE提供**知识检索增强**能力：

| 功能 | 说明 |
|------|------|
| **文档索引** | 将GO2SE文档/策略/信号索引 |
| **语义检索** | 理解自然语言查询 |
| **上下文注入** | 检索结果注入LLM上下文 |
| **持续更新** | 新数据自动更新索引 |

## 与GO2SE集成

```
用户查询 → RAG检索 → 相关上下文 → LLM生成 → 响应
```

| RAG组件 | GO2SE应用 |
|---------|-----------|
| 向量数据库 | 存储策略/信号/文档 |
| 嵌入模型 | 理解交易意图 |
| 检索器 | 找相关历史案例 |
| 上下文组装 | 增强LLM决策 |

## 技术架构

```
┌─────────────────────────────────────────────────┐
│                  RAG 系统                        │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐           │
│  │ 文档索引器  │ →  │ 向量数据库   │           │
│  │ (Ingest)   │    │ (ChromaDB)  │           │
│  └──────────────┘    └──────┬───────┘           │
│                             ↓                    │
│  ┌──────────────┐    ┌──────────────┐           │
│  │ 自然语言查询 │ →  │  语义检索    │           │
│  │ (Query)     │    │  (Similarity)│           │
│  └──────────────┘    └──────┬───────┘           │
│                             ↓                    │
│  ┌──────────────┐    ┌──────────────┐           │
│  │ 上下文组装   │ ←  │  Top-K 结果 │           │
│  │ (Context)   │    │            │           │
│  └──────┬───────┘    └──────────────┘           │
│         ↓                                         │
│  ┌──────────────┐                                │
│  │ LLM生成响应  │                                │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

## GO2SE知识库

| 知识类型 | 内容 | 索引字段 |
|---------|------|---------|
| **策略** | 7工具配置, 123趋势模型 | name, type, indicators |
| **信号** | 历史信号, 执行结果 | symbol, signal, confidence |
| **交易** | 持仓, 盈亏, 历史 | symbol, pnl, date |
| **配置** | API Keys, 风控规则 | name, value |
| **文档** | SPEC, 架构文档 | title, content |

## API端点

```bash
# 添加文档
POST /api/rag/ingest
{
  "text": "Rabbit策略使用EMA均线...",
  "metadata": {"type": "strategy", "name": "rabbit"}
}

# 检索
POST /api/rag/query
{
  "query": "Rabbit策略参数配置",
  "top_k": 5
}

# 删除
DELETE /api/rag/delete
{"ids": ["doc_id_1", "doc_id_2"]}

# 状态
GET /api/rag/status
```

## 安装依赖

```bash
# 向量数据库 (选择一种)
pip install chromadb          # 轻量级
pip install qdrant-client     # 生产级
pip install faiss-cpu         # Facebook出品

# 嵌入模型
pip install sentence-transformers

# RAG框架
pip install ragas             # 评测
pip install langchain         # 编排
```

## 使用示例

```python
from langchain.embeddings import SentenceTransformers
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

# 1. 文档分割
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = splitter.split_text(strategy_document)

# 2. 嵌入
embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. 索引
db = Chroma.from_texts(texts, embeddings, metadatas=[{"source": "strategy"}])

# 4. 检索
docs = db.similarity_search("Rabbit策略参数", k=5)

# 5. 上下文组装
context = "\n".join([doc.page_content for doc in docs])
```

## GO2SE RAG配置

```yaml
rag:
  vectorstore: chromadb  # or qdrant
  embedding: all-MiniLM-L6-v2
  
  index:
    strategies: true
    signals: true
    trades: true
    docs: true
    
  retrieval:
    top_k: 5
    similarity_threshold: 0.7
    
  update:
    interval: 3600  # 每小时更新
    on_new_data: true
```

## 与现有技能互补

| 技能 | 功能 | RAG增强 |
|------|------|---------|
| agentbrain | 云端记忆 | 本地知识检索 |
| memory-qdrant | 向量存储 | RAG检索 |
| evomap-tools | 众包知识 | 结构化知识 |

## 状态

| 组件 | 状态 |
|------|------|
| 文档结构 | ✅ 完成 |
| API设计 | ✅ 完成 |
| 向量数据库 | ⏳ 待安装 |
| 嵌入模型 | ⏳ 待安装 |
| 集成GO2SE | 🔄 开发中 |
