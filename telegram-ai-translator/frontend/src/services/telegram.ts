import WebApp from '@twa-dev/sdk'

export function initTelegram() {
  try {
    // 初始化 Telegram Web App
    WebApp.ready()
    
    // 设置主题参数
    WebApp.setHeaderColor('#0f0f23')
    WebApp.setBackgroundColor('#0f0f23')
    
    // 启用关闭按钮
    WebApp.enableClosingConfirmation()
    
    console.log('Telegram SDK initialized:', WebApp.initDataUnsafe)
  } catch (error) {
    console.log('Running outside Telegram')
  }
}

export function getUserInfo() {
  try {
    return WebApp.initDataUnsafe?.user
  } catch {
    return null
  }
}

export function shareToChat(text: string, url?: string) {
  try {
    const shareText = url ? `${text}\n${url}` : text
    WebApp.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(shareText)}`)
  } catch (error) {
    console.error('Share failed:', error)
  }
}

export function showAlert(message: string) {
  try {
    WebApp.showAlert(message)
  } catch {
    alert(message)
  }
}

export function expandApp() {
  try {
    WebApp.expand()
  } catch {
    // ignore
  }
}
