import { useState, useEffect } from 'react'
import { getVideos, searchVideos, Video } from '../services/api'
import VideoCard from '../components/VideoCard'
import SearchBar from '../components/SearchBar'
import LanguageSelector from '../components/LanguageSelector'

interface HomePageProps {
  onPlayVideo: (url: string, title: string) => void
}

export default function HomePage({ onPlayVideo }: HomePageProps) {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLang, setSelectedLang] = useState('zh')

  useEffect(() => {
    loadVideos()
  }, [])

  const loadVideos = async () => {
    setLoading(true)
    try {
      const data = await getVideos()
      setVideos(data)
    } catch (error) {
      console.error('Failed to load videos:', error)
    }
    setLoading(false)
  }

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    if (query.trim()) {
      setLoading(true)
      try {
        const results = await searchVideos(query)
        setVideos(results)
      } catch (error) {
        console.error('Search failed:', error)
      }
      setLoading(false)
    } else {
      loadVideos()
    }
  }

  const categories = ['全部', '短剧', '演讲', '动漫', '韩剧', '教学', '搞笑']

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* 顶部标题 */}
      <header className="glass px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                SYN Vision TV
              </h1>
              <p className="text-xs text-gray-400">短视频 + AI翻译</p>
            </div>
          </div>
          <LanguageSelector 
            selected={selectedLang} 
            onChange={setSelectedLang} 
          />
        </div>
        
        <SearchBar 
          value={searchQuery}
          onChange={setSearchQuery}
          onSearch={handleSearch}
          placeholder="搜索视频..."
        />
      </header>

      {/* 分类标签 */}
      <div className="flex gap-2 px-4 py-3 overflow-x-auto scrollbar-hide">
        {categories.map((cat) => (
          <button
            key={cat}
            className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap transition-all ${
              cat === '全部' 
                ? 'bg-primary text-white' 
                : 'bg-card text-gray-400 hover:bg-primary/20'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* 视频列表 */}
      <main className="flex-1 overflow-y-auto px-4 pb-4">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {videos.map((video) => (
              <VideoCard 
                key={video.id} 
                video={video} 
                onClick={() => onPlayVideo(video.url, video.title)}
              />
            ))}
          </div>
        )}
        
        {videos.length === 0 && !loading && (
          <div className="text-center py-20">
            <p className="text-gray-400">暂无视频</p>
          </div>
        )}
      </main>

      {/* 底部提示 */}
      <footer className="px-4 py-2 text-center text-xs text-gray-500">
        点击视频开始播放 • AI实时翻译字幕
      </footer>
    </div>
  )
}
