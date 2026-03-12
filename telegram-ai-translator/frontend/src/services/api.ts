const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

export interface Video {
  id: string
  title: string
  url: string
  thumbnail: string
  duration: string
  views: number
  category: string
}

export interface Subtitle {
  id: string
  text: string
  translatedText: string
  startTime: number
  endTime: number
}

// 获取视频列表
export async function getVideos(): Promise<Video[]> {
  try {
    const res = await fetch(`${API_BASE}/videos`)
    return await res.json()
  } catch {
    // 返回示例数据
    return MOCK_VIDEOS
  }
}

// 解析视频URL (支持YouTube, TikTok等)
export async function parseVideoUrl(url: string): Promise<{ url: string; title: string }> {
  try {
    const res = await fetch(`${API_BASE}/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })
    return await res.json()
  } catch {
    // 如果API不可用，返回原始URL
    return { url, title: '视频' }
  }
}

// 获取翻译字幕
export async function getSubtitles(videoId: string): Promise<Subtitle[]> {
  try {
    const res = await fetch(`${API_BASE}/subtitles/${videoId}`)
    return await res.json()
  } catch {
    return []
  }
}

// AI翻译文字
export async function translateText(text: string, targetLang: string): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, targetLang })
    })
    const data = await res.json()
    return data.translatedText
  } catch {
    return text
  }
}

// 搜索视频
export async function searchVideos(query: string): Promise<Video[]> {
  try {
    const res = await fetch(`${API_BASE}/videos/search?q=${encodeURIComponent(query)}`)
    return await res.json()
  } catch {
    return MOCK_VIDEOS.filter(v => 
      v.title.toLowerCase().includes(query.toLowerCase())
    )
  }
}

// 示例数据
const MOCK_VIDEOS: Video[] = [
  {
    id: '1',
    title: '【短剧】霸道总裁爱上我 第一集',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/drama1/400/225',
    duration: '15:30',
    views: 12500,
    category: '短剧'
  },
  {
    id: '2',
    title: '英文演讲 - TED: 如何学习新语言',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/ted2/400/225',
    duration: '12:45',
    views: 8900,
    category: '演讲'
  },
  {
    id: '3',
    title: '日语动漫精彩片段合集',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/anime3/400/225',
    duration: '08:20',
    views: 23400,
    category: '动漫'
  },
  {
    id: '4',
    title: '韩剧经典台词 - 浪漫满屋',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/kdrama4/400/225',
    duration: '05:15',
    views: 15600,
    category: '韩剧'
  },
  {
    id: '5',
    title: '法语教学 - 日常对话',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/french5/400/225',
    duration: '10:00',
    views: 5600,
    category: '教学'
  },
  {
    id: '6',
    title: '【爆笑】搞笑集锦 第42期',
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    thumbnail: 'https://picsum.photos/seed/funny6/400/225',
    duration: '18:30',
    views: 45000,
    category: '搞笑'
  }
]
