import { Video } from '../services/api'

interface VideoCardProps {
  video: Video
  onClick: () => void
}

export default function VideoCard({ video, onClick }: VideoCardProps) {
  return (
    <div 
      onClick={onClick}
      className="bg-card rounded-xl overflow-hidden cursor-pointer transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/20"
    >
      {/* 缩略图 */}
      <div className="relative aspect-video bg-gray-800">
        <img 
          src={video.thumbnail} 
          alt={video.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        {/* 时长 */}
        <div className="absolute bottom-2 right-2 px-2 py-0.5 bg-black/70 rounded text-xs">
          {video.duration}
        </div>
        {/* 播放图标 */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black/30">
          <div className="w-12 h-12 rounded-full bg-primary/90 flex items-center justify-center">
            <svg className="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
      </div>
      
      {/* 信息 */}
      <div className="p-3">
        <h3 className="text-sm font-medium line-clamp-2 mb-2">{video.title}</h3>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="px-2 py-0.5 bg-primary/20 text-primary rounded">{video.category}</span>
          <span>{formatViews(video.views)}</span>
        </div>
      </div>
    </div>
  )
}

function formatViews(views: number): string {
  if (views >= 10000) {
    return `${(views / 10000).toFixed(1)}万播放`
  }
  return `${views}播放`
}
