# SYN Vision TV - 部署指南

## 前置要求

- Node.js 18+
- npm 或 yarn
- FFmpeg (用于视频处理，后端可选)

## 开发模式

### 1. 启动后端

```bash
cd backend
npm install
npm run dev
```

后端运行在 http://localhost:3001

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

## 生产部署

### 前端部署

可以使用 Vercel、Netlify 或 Cloudflare Pages:

```bash
cd frontend
npm run build
# 将 dist 目录部署到静态托管
```

### 后端部署

可以使用 Railway、Render、Docker 等:

```bash
cd backend
npm install
npm run build
npm start
```

## Telegram Bot 配置

1. 创建 Telegram Bot: @BotFather
2. 获取 Bot Token
3. 创建 Mini App:
   - 部署前端到 HTTPS 域名
   - 使用 /newapp 命令创建
   - 填写 Mini App URL

## 环境变量

后端支持以下环境变量:

```
PORT=3001
OPENAI_API_KEY=sk-xxx  # 可选，用于GPT翻译
```

## 功能说明

### 视频播放
- 支持 HLS 流媒体
- 支持 MP4 直接播放
- 支持 YouTube/TikTok 解析 (需配置 yt-dlp)

### AI翻译
- 免费方案: MyMemory API (每分钟1000字符限制)
- 付费方案: OpenAI GPT API

### 语音识别 (待实现)
- 使用 OpenAI Whisper API
- 或使用 Faster Whisper 本地部署
