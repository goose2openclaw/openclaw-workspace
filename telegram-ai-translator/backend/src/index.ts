import express from 'express'
import cors from 'cors'
import { videoRouter } from './routes/video.js'
import { parseRouter } from './routes/parse.js'
import { translateRouter } from './routes/translate.js'

const app = express()
const PORT = process.env.PORT || 3001

// 中间件
app.use(cors())
app.use(express.json())

// 路由
app.use('/api/videos', videoRouter)
app.use('/api/parse', parseRouter)
app.use('/api/translate', translateRouter)

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 服务器运行在 http://localhost:${PORT}`)
  console.log(`📡 API端点:`)
  console.log(`   - GET  /api/videos      视频列表`)
  console.log(`   - POST /api/parse       解析视频URL`)
  console.log(`   - POST /api/translate  翻译文本`)
})
