import { useState, useRef, useEffect, useCallback } from 'react'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import { getSubtitles, translateText, Subtitle } from '../services/api'
import { shareToChat, expandApp } from '../services/telegram'
import SubtitleDisplay from '../components/SubtitleDisplay'

interface VideoPageProps {
  url: string
  title: string
  onBack: () => void
}

export default function VideoPage({ url, title, onBack }: VideoPageProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<Plyr | null>(null)
  
  const [showSubtitles, setShowSubtitles] = useState(true)
  const [targetLang, setTargetLang] = useState('zh')
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [currentSubtitle, setCurrentSubtitle] = useState<Subtitle | null>(null)
  const [isTranslating, setIsTranslating] = useState(false)
  const [translationEnabled, setTranslationEnabled] = useState(true)

  // 初始化播放器
  useEffect(() => {
    if (videoRef.current) {
      playerRef.current = new Plyr(videoRef.current, {
        controls: [
          'play-large',
          'play',
          'progress',
          'current-time',
          'mute',
          'volume',
          'captions',
          'settings',
          'pip',
          'fullscreen',
        ],
        settings: ['captions', 'quality', 'speed'],
        autoplay: true,
      })

      // 监听时间更新，同步字幕
      playerRef.current.on('timeupdate', () => {
        if (playerRef.current) {
          const currentTime = playerRef.current.currentTime
          const subtitle = subtitles.find(
            s => currentTime >= s.startTime && currentTime <= s.endTime
          )
          setCurrentSubtitle(subtitle || null)
        }
      })
    }

    return () => {
      playerRef.current?.destroy()
    }
  }, [url])

  // 加载字幕
  useEffect(() => {
    loadSubtitles()
  }, [title])

  const loadSubtitles = async () => {
    // 模拟字幕数据
    const mockSubtitles: Subtitle[] = [
      { id: '1', text: 'Hello everyone, welcome to our program.', translatedText: '大家好，欢迎来到我们的节目。', startTime: 0, endTime: 3 },
      { id: '2', text: 'Today we are going to talk about artificial intelligence.', translatedText: '今天我们要讨论人工智能。', startTime: 3, endTime: 6 },
      { id: '3', text: 'AI is changing the world in many ways.', translatedText: 'AI正在以多种方式改变世界。', startTime: 6, endTime: 10 },
      { id: '4', text: 'From healthcare to education, from transportation to entertainment.', translatedText: '从医疗到教育，从交通到娱乐。', startTime: 10, endTime: 15 },
      { id: '5', text: 'Let us explore the future together.', translatedText: '让我们一起探索未来。', startTime: 15, endTime: 18 },
    ]
    setSubtitles(mockSubtitles)
  }

  // 实时翻译功能
  const handleTranslate = useCallback(async () => {
    if (!currentSubtitle || !translationEnabled) return
    
    setIsTranslating(true)
    try {
      const translated = await translateText(currentSubtitle.text, targetLang)
      setSubtitles(prev => prev.map(s => 
        s.id === currentSubtitle.id 
          ? { ...s, translatedText: translated } 
          : s
      ))
    } catch (error) {
      console.error('Translation failed:', error)
    }
    setIsTranslating(false)
  }, [currentSubtitle, targetLang, translationEnabled])

  // 当字幕变化时自动翻译
  useEffect(() => {
    if (currentSubtitle && translationEnabled && !currentSubtitle.translatedText.includes('翻译中')) {
      handleTranslate()
    }
  }, [currentSubtitle?.id])

  const togglePlay = () => {
    playerRef.current?.togglePlay()
  }

  const handleShare = () => {
    shareToChat(title, window.location.href)
  }

  return (
    <div className="h-full flex flex-col bg-black">
      {/* 视频播放器区域 */}
      <div className="relative bg-black" style={{ aspectRatio: '16/9' }}>
        <video
          ref={videoRef}
          className="plyr-video"
          playsInline
          crossOrigin="anonymous"
          src={url}
          poster=""
        />
        
        {/* 自定义字幕显示 */}
        {showSubtitles && currentSubtitle && (
          <SubtitleDisplay
            original={currentSubtitle.text}
            translated={translationEnabled ? currentSubtitle.translatedText : ''}
            isTranslating={isTranslating}
          />
        )}

        {/* 返回按钮 */}
        <button
          onClick={onBack}
          className="absolute top-4 left-4 w-10 h-10 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center z-10"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="white">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        {/* 视频信息 */}
        <div className="absolute bottom-16 left-4 right-4 z-10">
          <h2 className="text-white text-lg font-semibold drop-shadow-lg">{title}</h2>
        </div>
      </div>

      {/* 控制面板 */}
      <div className="flex-1 bg-dark p-4 overflow-y-auto">
        {/* 翻译控制 */}
        <div className="glass rounded-xl p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold flex items-center gap-2">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
              AI翻译
            </h3>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={translationEnabled}
                onChange={(e) => setTranslationEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {translationEnabled && (
            <div className="flex gap-2">
              {['zh', 'en', 'ja', 'ko'].map(lang => (
                <button
                  key={lang}
                  onClick={() => setTargetLang(lang)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                    targetLang === lang 
                      ? 'bg-primary text-white' 
                      : 'bg-card text-gray-400 hover:bg-card/80'
                  }`}
                >
                  {lang === 'zh' ? '中文' : lang === 'en' ? 'English' : lang === 'ja' ? '日本語' : '한국어'}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 字幕显示开关 */}
        <div className="glass rounded-xl p-4 mb-4">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              显示字幕
            </span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={showSubtitles}
                onChange={(e) => setShowSubtitles(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
            </label>
          </div>
        </div>

        {/* 分享按钮 */}
        <button
          onClick={handleShare}
          className="w-full btn-gradient flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          分享给朋友
        </button>
      </div>
    </div>
  )
}
