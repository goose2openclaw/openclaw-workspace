import { useState, useEffect } from 'react'
import { WebApp } from '@twa-dev/sdk'
import HomePage from './pages/HomePage'
import VideoPage from './pages/VideoPage'
import { initTelegram } from './services/telegram'

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'video'>('home')
  const [videoUrl, setVideoUrl] = useState<string>('')
  const [videoTitle, setVideoTitle] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 初始化 Telegram SDK
    initTelegram()
    setIsLoading(false)
  }, [])

  const handlePlayVideo = (url: string, title: string) => {
    setVideoUrl(url)
    setVideoTitle(title)
    setCurrentPage('video')
    
    // 扩展到全屏
    if (WebApp) {
      WebApp.expand()
    }
  }

  const handleBack = () => {
    setCurrentPage('home')
    if (WebApp) {
      WebApp.ready()
    }
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-dark">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-dark">
      {currentPage === 'home' ? (
        <HomePage onPlayVideo={handlePlayVideo} />
      ) : (
        <VideoPage 
          url={videoUrl} 
          title={videoTitle} 
          onBack={handleBack} 
        />
      )}
    </div>
  )
}

export default App
