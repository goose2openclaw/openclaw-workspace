"""
GO2SE RAG Engine - Lightweight Retrieval-Augmented Generation
基于TF-IDF和余弦相似度的轻量级RAG引擎
"""

import json
import hashlib
import os
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class RAGEngine:
    """轻量级RAG引擎 - 无需额外依赖"""
    
    def __init__(self, storage_path: str = "./data/rag"):
        self.storage_path = storage_path
        self.documents = []
        self.vectors = None
        self.vocab = {}
        self.idf = {}
        os.makedirs(storage_path, exist_ok=True)
        
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        return text.lower().split()
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算词频"""
        counter = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in counter.items()}
    
    def _compute_idf(self, docs: List[List[str]]) -> Dict[str, float]:
        """计算IDF"""
        N = len(docs)
        idf = {}
        vocab = set()
        for doc in docs:
            vocab.update(doc)
        for word in vocab:
            df = sum(1 for doc in docs if word in doc)
            idf[word] = np.log(N / (df + 1)) + 1
        return idf
    
    def _compute_tfidf(self, tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        """计算TF-IDF"""
        tf = self._compute_tf(tokens)
        return {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """计算余弦相似度"""
        all_words = set(vec1.keys()) | set(vec2.keys())
        if not all_words:
            return 0.0
        
        v1 = np.array([vec1.get(w, 0) for w in all_words])
        v2 = np.array([vec2.get(w, 0) for w in all_words])
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(v1, v2) / (norm1 * norm2)
    
    def ingest(self, text: str, metadata: Dict = None) -> str:
        """索引文档"""
        doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
        tokens = self._tokenize(text)
        
        doc = {
            "id": doc_id,
            "text": text,
            "tokens": tokens,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        self.documents.append(doc)
        
        # 更新IDF
        if len(self.documents) == 1:
            self.idf = self._compute_idf([tokens])
        else:
            all_docs = [d["tokens"] for d in self.documents]
            self.idf = self._compute_idf(all_docs)
        
        self._save()
        return doc_id
    
    def query(self, query: str, top_k: int = 5) -> List[Dict]:
        """检索相关文档"""
        if not self.documents:
            return []
        
        query_tokens = self._tokenize(query)
        query_tfidf = self._compute_tfidf(query_tokens, self.idf)
        
        results = []
        for doc in self.documents:
            doc_tfidf = self._compute_tfidf(doc["tokens"], self.idf)
            similarity = self._cosine_similarity(query_tfidf, doc_tfidf)
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "similarity": float(similarity)
            })
        
        # 排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def delete(self, doc_id: str) -> bool:
        """删除文档"""
        for i, doc in enumerate(self.documents):
            if doc["id"] == doc_id:
                self.documents.pop(i)
                self._save()
                return True
        return False
    
    def _save(self):
        """保存到磁盘"""
        path = os.path.join(self.storage_path, "documents.json")
        with open(path, "w") as f:
            json.dump({
                "documents": self.documents,
                "idf": self.idf
            }, f, ensure_ascii=False)
    
    def load(self):
        """从磁盘加载"""
        path = os.path.join(self.storage_path, "documents.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
                self.idf = data.get("idf", {})
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_documents": len(self.documents),
            "vocab_size": len(self.idf),
            "storage_path": self.storage_path
        }


# GO2SE 知识库预填充
def init_go2se_knowledge(rag: RAGEngine):
    """初始化GO2SE知识库"""
    
    knowledge_base = [
        {
            "text": "🐰 打兔子策略: 前20主流加密货币趋势追踪, 使用EMA均线判断趋势方向, RSI在40-70区间时入场, 止损5%, 止盈8%",
            "metadata": {"type": "strategy", "tool": "rabbit", "category": "trend"}
        },
        {
            "text": "🐹 打地鼠策略: 非主流币异动扫描, 火控雷达监控成交量突增3倍和价格变化5%, RSI超卖时买入, 止损8%, 止盈15%",
            "metadata": {"type": "strategy", "tool": "mole", "category": "momentum"}
        },
        {
            "text": "🔮 走着瞧策略: 预测市场决策, MiroFish 450智能体仿真, 胜率>65%时执行, 止损5%, 止盈10%",
            "metadata": {"type": "strategy", "tool": "oracle", "category": "prediction"}
        },
        {
            "text": "👑 跟大哥策略: 做市商协作, 监控订单簿和资金费率, 价差0.1%-1%时开仓, 止损3%, 止盈6%",
            "metadata": {"type": "strategy", "tool": "leader", "category": "market_making"}
        },
        {
            "text": "🍀 搭便车策略: 跟单交易, 选择胜率>55%、交易数>100的Trader, 最大回撤<20%",
            "metadata": {"type": "strategy", "tool": "hitchhiker", "category": "copy_trading"}
        },
        {
            "text": "💰 薅羊毛策略: 空投猎手, 只读API不授权钱包, 定期扫描新项目, 止损2%, 止盈20%",
            "metadata": {"type": "strategy", "tool": "airdrop", "category": "airdrop"}
        },
        {
            "text": "👶 穷孩子策略: 众包任务, EvoMap社交圈, 隔离保护, 止损1%, 止盈30%",
            "metadata": {"type": "strategy", "tool": "crowdsource", "category": "crowdsource"}
        },
        {
            "text": "MiroFish: 450个AI智能体×5轮共识仿真, 对投资决策进行仿真验证, 置信度>70%时执行",
            "metadata": {"type": "core", "component": "mirofish", "category": "simulation"}
        },
        {
            "text": "声纳库123趋势模型: 趋势类30个(EMA/SMA), 动量类25个(RSI/MACD), 波动类20个(Bollinger/ATR)",
            "metadata": {"type": "indicator", "name": "sonar_123", "category": "technical"}
        },
        {
            "text": "风控规则: 仓位>80%熔断, 日亏损>15%熔断, 单笔风险>5%拒绝, API错误率>1%降级",
            "metadata": {"type": "risk", "category": "rules"}
        }
    ]
    
    for item in knowledge_base:
        rag.ingest(item["text"], item["metadata"])
    
    return len(knowledge_base)


# 导出
RAG = RAGEngine
