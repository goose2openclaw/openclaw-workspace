/**
 * 🪿 Loading Screen - 优雅浮水天鹅
 */

import { useState, useEffect } from 'react'

type Theme = 'dark' | 'light'

export function LoadingScreen() {
  const [theme, setTheme] = useState<Theme>('dark')
  const [progress, setProgress] = useState(0)
  
  useEffect(() => {
    const hour = new Date().getHours()
    setTheme(hour < 6 || hour >= 18 ? 'dark' : 'light')
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval)
          return 100
        }
        const remaining = 100 - p
        return p + remaining * 0.05
      })
    }, 350)
    return () => clearInterval(interval)
  }, [])

  const isDark = theme === 'dark'

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: isDark
        ? 'linear-gradient(180deg, #0a1628 0%, #0f2844 50%, #0a1628 100%)'
        : 'linear-gradient(180deg, #e8f4fc 0%, #d0e8f5 50%, #e8f4fc 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      
      {/* 星光/水光 */}
      {[...Array(12)].map((_, i) => (
        <div key={i} style={{
          position: 'absolute',
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 30}%`,
          width: isDark ? `${1 + Math.random() * 2}px` : `${2 + Math.random() * 2}px`,
          height: isDark ? `${1 + Math.random() * 2}px` : `${2 + Math.random() * 2}px`,
          borderRadius: '50%',
          background: isDark ? `rgba(255,255,255,${0.3 + Math.random() * 0.5})` : `rgba(255,255,255,${0.6 + Math.random() * 0.4})`,
          animation: `twinkle ${2 + Math.random() * 3}s ease-in-out infinite`,
          animationDelay: `${Math.random() * 2}s`,
        }} />
      ))}

      {/* 水波 */}
      {[...Array(4)].map((_, i) => (
        <div key={`wave-${i}`} style={{
          position: 'absolute',
          bottom: `${i * 10}px`,
          left: 0,
          right: 0,
          height: '40px',
          background: isDark
            ? `linear-gradient(180deg, rgba(0,100,150,${0.04 + i * 0.02}) 0%, transparent 100%)`
            : `linear-gradient(180deg, rgba(100,180,220,${0.08 + i * 0.04}) 0%, transparent 100%)`,
          animation: `waterWave ${2.5 + i * 0.3}s ease-in-out infinite`,
          animationDelay: `${i * 0.1}s`,
        }} />
      ))}

      {/* 小鱼 */}
      {[...Array(4)].map((_, i) => (
        <div key={`fish-${i}`} style={{
          position: 'absolute',
          left: '-30px',
          top: `${30 + i * 12}%`,
          fontSize: `${1 + Math.random() * 0.3}rem`,
          animation: `fishSwim ${6 + Math.random() * 3}s linear infinite`,
          animationDelay: `${i * 1}s`,
          opacity: 0.4 + Math.random() * 0.4,
        }}>
          🐟
        </div>
      ))}

      {/* 涟漪 */}
      {[...Array(2)].map((_, i) => (
        <div key={`ripple-${i}`} style={{
          position: 'absolute',
          bottom: '50px',
          left: '50%',
          marginLeft: '-60px',
          width: '120px',
          height: '14px',
          borderRadius: '50%',
          border: `1px solid ${isDark ? 'rgba(0,150,200,0.1)' : 'rgba(255,255,255,0.2)'}`,
          animation: `rippleExpand ${3}s ease-out infinite`,
          animationDelay: `${i * 0.7}s`,
        }} />
      ))}

      <div style={{ position: 'relative', zIndex: 10, textAlign: 'center' }}>
        
        {/* 超大美丽天鹅 Emoji - 优雅浮水 */}
        <div style={{ 
          fontSize: '8rem', 
          margin: '0 auto 20px',
          lineHeight: 1,
          filter: isDark 
            ? 'drop-shadow(0 10px 30px rgba(0,150,200,0.3))' 
            : 'drop-shadow(0 10px 30px rgba(0,100,150,0.2))',
          animation: 'swanFloat 4s ease-in-out infinite',
        }}>
          🪿
        </div>

        {/* 标题 */}
        <h1 style={{
          fontSize: '2.75rem',
          fontWeight: 800,
          color: isDark ? '#f0f5f8' : '#1a3a5a',
          marginBottom: '6px',
          letterSpacing: '-0.02em',
          fontFamily: 'Georgia, serif',
        }}>
          Go2Se 护食的小天鹅
        </h1>

        <p style={{
          fontSize: '1rem',
          color: isDark ? 'rgba(150,180,200,0.9)' : 'rgba(40,80,120,0.9)',
          marginBottom: '8px',
          fontWeight: 500,
        }}>
          薅羊毛众包AI赚钱及Crypto量化投资平台
        </p>

        {/* 进度条 */}
        <div style={{ width: '260px', margin: '30px auto 12px' }}>
          <div style={{
            height: '4px',
            background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,50,100,0.1)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}>
            <div style={{
              height: '100%',
              width: `${progress}%`,
              background: isDark 
                ? 'linear-gradient(90deg, #00a5cf, #00d4aa, #7c3aed, #00a5cf)' 
                : 'linear-gradient(90deg, #0891b2, #0ea5e9, #6366f1, #0891b2)',
              backgroundSize: '300% 100%',
              borderRadius: '2px',
              animation: 'shimmerMove 1.5s linear infinite',
            }} />
          </div>
        </div>

        <p style={{
          fontSize: '0.875rem',
          fontWeight: 600,
          color: isDark ? '#00b5d6' : '#0891b2',
        }}>
          🦢 红掌拨清波ing... {Math.round(progress)}%
        </p>
      </div>

      {/* 底部 */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        display: 'flex',
        gap: '16px',
        fontSize: '0.625rem',
        color: isDark ? 'rgba(150,180,200,0.5)' : 'rgba(40,80,120,0.5)',
      }}>
        <span>🤖 AI智能</span>
        <span>📊 量化</span>
        <span>🛡️ 风控</span>
      </div>

      <style>{`
        @keyframes twinkle { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
        @keyframes waterWave { 0%, 100% { transform: translateX(-3px); } 50% { transform: translateX(3px); } }
        @keyframes rippleExpand { 0% { transform: scale(0.3); opacity: 0.6; } 100% { transform: scale(1.5); opacity: 0; } }
        @keyframes fishSwim { 0% { transform: translateX(-30px); } 100% { transform: translateX(calc(100vw + 30px)); } }
        @keyframes shimmerMove { 0% { background-position: 300% 0; } 100% { background-position: -300% 0; } }
        @keyframes swanFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
      `}</style>
    </div>
  )
}
