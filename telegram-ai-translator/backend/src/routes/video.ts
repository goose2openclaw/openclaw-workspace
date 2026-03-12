import { Router } from 'express'

export const videoRouter = Router()

// 模拟视频数据
const videos = [
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

// 获取视频列表
videoRouter.get('/', (req, res) => {
  const { category, q } = req.query
  
  let result = [...videos]
  
  if (category && category !== '全部') {
    result = result.filter(v => v.category === category)
  }
  
  if (q) {
    const query = (q as string).toLowerCase()
    result = result.filter(v => v.title.toLowerCase().includes(query))
  }
  
  res.json(result)
})

// 获取单个视频
videoRouter.get('/:id', (req, res) => {
  const video = videos.find(v => v.id === req.params.id)
  if (!video) {
    return res.status(404).json({ error: '视频不存在' })
  }
  res.json(video)
})

// 搜索视频
videoRouter.get('/search', (req, res) => {
  const { q } = req.query
  if (!q) {
    return res.json([])
  }
  
  const query = (q as string).toLowerCase()
  const results = videos.filter(v => v.title.toLowerCase().includes(query))
  res.json(results)
})
