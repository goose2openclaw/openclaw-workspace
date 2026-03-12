# SYN Vision TV - 短视频播放 + AI翻译 Telegram小程序

## 1. 项目概述

- **项目名称**: SYN Vision TV (类似新维视界)
- **项目类型**: Telegram Mini App (小程序)
- **核心功能**: 在Telegram内播放短视频/短剧 + AI实时翻译字幕
- **目标用户**: 喜欢观看海外短视频/短剧的中文用户

## 2. 功能规范

### 2.1 视频播放模块
- [ ] 支持直接URL播放 (MP4, HLS)
- [ ] 支持YouTube/TikTok视频解析播放
- [ ] 视频播放器控件 (播放/暂停, 进度条, 全屏, 音量)
- [ ] 弹幕功能 (可选)
- [ ] 投屏支持 (DLNA)

### 2.2 AI翻译模块
- [ ] 语音识别 (ASR) - 提取视频语音文字
- [ ] 实时翻译 - 将识别文字翻译为目标语言
- [ ] 双语字幕显示 - 原文 + 译文
- [ ] 字幕样式自定义 (字体, 大小, 颜色, 背景)
- [ ] 支持语言: 中文 ↔ English ↔ 日语 ↔ 韩语 等

### 2.3 用户交互
- [ ] 视频列表/推荐
- [ ] 搜索功能
- [ ] 收藏/历史记录
- [ ] 分享功能

### 2.4 后端功能
- [ ] 视频URL解析服务
- [ ] AI翻译API集成 (OpenAI Whisper + GPT)
- [ ] 用户数据存储

## 3. 技术栈

### 前端
- **框架**: React + TypeScript
- **样式**: Tailwind CSS
- **视频播放器**: video.js 或 plyr
- **Telegram**: @twa-dev/sdk

### 后端
- **框架**: Node.js + Express
- **AI服务**: 
  - 语音识别: OpenAI Whisper API / Faster Whisper (本地)
  - 翻译: OpenAI GPT API / 免费方案 (Google Translate, DeepL)
- **视频解析**: yt-dlp, tiktok-api

## 4. 项目结构

```
telegram-ai-translator/
├── frontend/                 # Telegram小程序前端
│   ├── src/
│   │   ├── components/       # UI组件
│   │   ├── pages/           # 页面
│   │   ├── hooks/           # React hooks
│   │   ├── services/        # API服务
│   │   ├── utils/           # 工具函数
│   │   └── App.tsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                  # 后端服务
│   ├── src/
│   │   ├── routes/          # API路由
│   │   ├── services/        # 业务逻辑
│   │   ├── utils/           # 工具
│   │   └── index.ts
│   └── package.json
│
└── README.md
```

## 5. 核心功能实现思路

### 视频播放
使用 `plyr` 或 `video.js` 实现统一播放器，支持:
- HLS流媒体播放
- MP4点播
- 集成Telegram播放器API

### AI翻译流程
1. **视频 → 音频提取**: 使用ffmpeg提取音频
2. **音频 → 文字**: Whisper API实时语音识别
3. **文字 → 翻译**: GPT API翻译或免费翻译API
4. **字幕渲染**: 同步显示原文+译文

### Telegram集成
- 使用 @twa-dev/sdk 与Telegram交互
- 获取用户信息
- 分享到聊天
- 主题适配
