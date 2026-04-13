# 免费替代方案配置

## 已验证免费方案（无需API Key）

### 1. 网页搜索 ✅
```bash
# 使用 multi-search-engine（17个引擎，无key）
# 使用 exa-web-search-free（Exa神经搜索，无key）
```

### 2. A股数据 ✅
```python
import akshare as ak
# stock_zh_a_spot_em() - 实时行情
# stock_zh_a_hist() - 历史K线
# 无需任何token或key
```

### 3. 语音识别（免费方案）✅
- **浏览器端**: Web Speech API (`webkitSpeechRecognition`) - 已集成到 voice-widget.html
- **桌面端**: 浏览器原生，免费，无需网络

### 4. 新闻/社交洞察 ✅
```bash
# social-insights - 已安装
```

## 需要付费API的服务（无免费替代）

| 服务 | 官方方案 | 备注 |
|------|---------|------|
| Notion | 需 NOTION_API_KEY | 笔记 |
| TuShare Pro | 需 TUSHARE_TOKEN | 付费数据更全 |
| Tavily Search | 需 API Key | 但有 multi-search-engine 替代 |
| OpenAI Whisper API | 需 OPENAI_API_KEY | 用浏览器Web Speech API替代 |

## 技能优化状态

| 技能 | 状态 | 方案 |
|------|------|------|
| akshare-stock | ✅ 可用 | AkShare免费 |
| multi-search-engine | ✅ 可用 | 17个搜索引擎 |
| exa-web-search-free | ✅ 可用 | Exa神经搜索 |
| social-insights | ✅ 可用 | 新闻聚合 |
| openai-whisper | ⚠️ 需binary | 用Web Speech API替代 |
| openclaw-tavily-search | ⚠️ 需key | 用multi-search-engine替代 |
| notion | ❌ 需API Key | 暂无免费替代 |
