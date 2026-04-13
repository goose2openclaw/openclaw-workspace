# 🎙️ OpenClaw 语音输入 - 控制台侧边栏集成版

## 快速开始（3种方式）

### 方式一：独立窗口（推荐，最稳定）

```bash
# 直接在浏览器中打开
open /root/.openclaw/workspace/openclaw-voice-input/voice-widget.html

# 或在控制台新标签页打开
# http://127.0.0.1:18789/ → 新标签 → 
# file:///root/.openclaw/workspace/openclaw-voice-input/voice-widget.html
```

然后把窗口放到屏幕角落，最小化，语音输入时打开即可。

---

### 方式二：浏览器书签（一键打开）

在浏览器中创建新书签，名称填 `🎙️ 语音输入`，URL 填以下代码：

```javascript
javascript:(function(){var w=window.open('file:///root/.openclaw/workspace/openclaw-voice-input/voice-widget.html','_blank','width=380,height=560,top=100,left=100,toolbar=no,menubar=no');})()
```

之后在控制台任意页面点击书签即可打开语音面板。

---

### 方式三：控制台内悬浮（进阶）

将以下代码粘贴到控制台 **DevTools → Console**（仅当前会话有效）：

```javascript
(function(){
  if(window.__VOICE_WIDGET_LOADED__)return;
  var iframe=document.createElement('iframe');
  iframe.src='file:///root/.openclaw/workspace/openclaw-voice-input/voice-widget.html';
  iframe.style.cssText='position:fixed;bottom:20px;right:20px;width:340px;height:0;border:none;z-index:99999;transition:height 0.3s';
  iframe.id='voice-widget-frame';
  document.body.appendChild(iframe);
  window.__VOICE_WIDGET_LOADED__=true;
  // 注入 toggle 按钮
  var btn=document.createElement('button');
  btn.textContent='🎙️';
  btn.style.cssText='position:fixed;bottom:24px;right:24px;z-index:99998;width:48px;height:48px;border-radius:50%;border:none;background:#0f1419;color:#00d4aa;font-size:20px;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,0.5);';
  btn.onclick=function(){var f=document.getElementById('voice-widget-frame');if(f.style.height==='0px'||f.style.height===''){f.style.height='520px';}else{f.style.height='0px';}};
  document.body.appendChild(btn);
  console.log('[Voice Widget] ✓ 已加载，快捷键：无（点击按钮打开）');
})();
```

---

## 功能说明

| 功能 | 快捷键 |
|------|--------|
| 打开/关闭面板 | `V` 键 |
| 按住录音 | `空格键`（焦点在空白区域时）|
| 松手自动识别 | — |
| 复制文字 | 点击复制按钮 |

---

## 两种识别模式

| 模式 | API Key | 准确率 | 费用 |
|------|---------|--------|------|
| 🌐 **浏览器原生** | 不需要 | 中等 | 免费 |
| 🤖 **Whisper API** | 需要 | 高 | 按量付费 |

---

## 文件结构

```
openclaw-voice-input/
├── README.md              ← 本文件
├── voice-widget.html      ← 独立悬浮窗版本（推荐）
├── voice-input.html      ← 全功能独立页面版
└── inject-widget.js      ← 控制台注入脚本（进阶）
```

---

## 技术原理

voice-widget.html 使用 **iframe 隔离** 技术：
- 不依赖 OpenClaw 源码
- 不修改任何 OpenClaw 文件
- 在任意页面浮动显示
- 与页面 JS 隔离，避免冲突

---

## 已知限制

1. 浏览器原生语音识别不支持 Safari（推荐用 Whisper API）
2. 独立窗口模式需要在标签页间切换
3. file:// 协议在某些浏览器中有权限限制（推荐 Whisper API 模式）

---

## 下一步优化

如需深度集成（如加到控制台侧边栏），需要修改 OpenClaw 源码或开发官方插件。目前 OpenClaw 插件系统不支持 UI 扩展。
