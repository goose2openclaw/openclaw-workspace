import { Router } from 'express'

export const parseRouter = Router()

// 解析视频URL
parseRouter.post('/', async (req, res) => {
  const { url } = req.body
  
  if (!url) {
    return res.status(400).json({ error: 'URL不能为空' })
  }
  
  try {
    // 简单的URL检测和转换
    let videoUrl = url
    let title = '视频'
    
    // YouTube 处理 (需要 yt-dlp 或类似工具)
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      // 这里可以集成 yt-dlp
      // videoUrl = await getYouTubeStream(url)
      title = 'YouTube视频'
    }
    
    // TikTok 处理
    else if (url.includes('tiktok.com')) {
      title = 'TikTok视频'
    }
    
    // 直接返回原始URL (假设是可直接播放的)
    res.json({
      url: videoUrl,
      title
    })
  } catch (error) {
    console.error('解析失败:', error)
    res.status(500).json({ error: '解析失败' })
  }
})

// 获取支持的平台列表
parseRouter.get('/platforms', (req, res) => {
  res.json({
    platforms: [
      { name: 'YouTube', icon: '🎬' },
      { name: 'TikTok', icon: '🎵' },
      { name: '抖音', icon: '📱' },
      { name: 'Twitter/X', icon: '🐦' },
      { name: 'Instagram', icon: '📷' },
      { name: 'Facebook', icon: '👥' }
    ]
  })
})
