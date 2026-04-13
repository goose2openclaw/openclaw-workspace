/**
 * OpenClaw Voice Widget - Auto-inject Script
 * 
 * 自动注入到 OpenClaw 控制台页面
 * 
 * 使用方式：
 * 1. 将此文件URL配置为浏览器书签
 * 2. 或在控制台DevTools中直接粘贴运行
 * 3. 或通过插件系统自动加载
 * 
 * 自动检测 Control UI 页面并加载语音输入组件
 */

(function() {
  'use strict';

  // 防止重复注入
  if (window.__VOICE_WIDGET_LOADED__) return;
  window.__VOICE_WIDGET_LOADED__ = true;

  const WIDGET_URL = 'file:///root/.openclaw/workspace/openclaw-voice-input/voice-widget.html';
  const INJECT_ATTR = 'data-voice-widget-injected';

  function injectWidget() {
    // 检测是否已注入
    if (document.getElementById('voiceToggle') || document.body.hasAttribute(INJECT_ATTR)) {
      return;
    }

    // 加载 widget iframe
    const iframe = document.createElement('iframe');
    iframe.id = 'voice-widget-frame';
    iframe.src = WIDGET_URL;
    iframe.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 0;
      height: 0;
      border: none;
      visibility: hidden;
      pointer-events: none;
      z-index: -1;
    `;
    iframe.setAttribute(INJECT_ATTR, 'true');
    document.body.appendChild(iframe);

    // 监听 iframe 加载
    iframe.addEventListener('load', () => {
      console.log('[Voice Widget] ✓ 已加载到控制台');
    });

    iframe.addEventListener('error', () => {
      console.warn('[Voice Widget] 加载失败，请检查文件路径是否可访问');
    });
  }

  // 立即尝试注入
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    injectWidget();
  } else {
    document.addEventListener('DOMContentLoaded', injectWidget);
  }

  // 监听页面变化（控制台是 SPA，路由变化不会刷新页面）
  let observer = null;
  function startObserver() {
    if (observer) return;
    observer = new MutationObserver(() => {
      if (!document.getElementById('voice-widget-frame')) {
        injectWidget();
      }
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === 'complete') {
    startObserver();
  } else {
    window.addEventListener('load', startObserver);
  }

  // 打印加载状态
  console.log('%c🎙️ Voice Widget', 'background:#0a0e17;color:#00d4aa;padding:4px 8px;border-radius:4px;font-weight:bold', '加载中...');
  console.log('[Voice Widget] 快捷键: V 打开/关闭 | 空格键 录音');

})();
