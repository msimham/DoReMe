"use client";

import { FeedItem } from "@/lib/types";
import { Heart, MessageCircle, Share2 } from "lucide-react";
import { useState } from "react";

interface FeedCardProps {
  item: FeedItem;
}

export default function FeedCard({ item }: FeedCardProps) {
  const [liked, setLiked] = useState(false);

  const handleLike = () => {
    setLiked(!liked);
    // Could show a toast here
  };

  const handleComment = () => {
    alert("Comment feature coming soon!");
  };

  const handleShare = () => {
    alert("Share feature coming soon!");
  };

  const getYouTubeEmbedUrl = (url: string) => {
    const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/)?.[1];
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
  };

  const embedUrl = item.videoUrl ? getYouTubeEmbedUrl(item.videoUrl) : null;

  return (
    <div className="card p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 bg-black/5 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-medium">{item.creatorName[0]}</span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm">{item.creatorName}</h3>
          <p className="text-xs text-black/50">{item.handle}</p>
          {item.location && (
            <p className="text-xs text-black/40 mt-0.5">{item.location}</p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">{item.title}</h4>
        {item.description && (
          <p className="text-sm text-black/70 mb-3">{item.description}</p>
        )}

        {/* Video */}
        {embedUrl ? (
          <div className="relative w-full aspect-video bg-black/5 rounded-lg overflow-hidden">
            <iframe
              src={embedUrl}
              className="absolute inset-0 w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        ) : item.thumbnailUrl ? (
          <div className="relative w-full aspect-video bg-black/5 rounded-lg overflow-hidden">
            <img
              src={item.thumbnailUrl}
              alt={item.title}
              className="w-full h-full object-cover"
            />
          </div>
        ) : null}

        {/* Tags */}
        {item.tags && item.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {item.tags.map((tag) => (
              <span key={tag} className="chip text-xs">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-6 pt-4 border-t border-black/5">
        <button
          onClick={handleLike}
          className={`flex items-center gap-2 text-sm transition-colors ${
            liked ? "text-red-500" : "text-black/60 hover:text-black"
          }`}
        >
          <Heart size={18} fill={liked ? "currentColor" : "none"} />
          <span>Like</span>
        </button>
        <button
          onClick={handleComment}
          className="flex items-center gap-2 text-sm text-black/60 hover:text-black transition-colors"
        >
          <MessageCircle size={18} />
          <span>Comment</span>
        </button>
        <button
          onClick={handleShare}
          className="flex items-center gap-2 text-sm text-black/60 hover:text-black transition-colors"
        >
          <Share2 size={18} />
          <span>Share</span>
        </button>
      </div>
    </div>
  );
}
