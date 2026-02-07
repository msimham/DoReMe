"use client";

import { Musician } from "@/lib/types";
import { X, Heart } from "lucide-react";

interface MatchCardProps {
  musician: Musician;
  onLike: () => void;
  onPass: () => void;
}

export default function MatchCard({ musician, onLike, onPass }: MatchCardProps) {
  return (
    <div className="card p-8 max-w-2xl w-full animate-scale-in">
      {/* Avatar */}
      <div className="flex items-start gap-6 mb-6">
        <div className="w-20 h-20 bg-black/5 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-2xl font-medium">{musician.name[0]}</span>
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold mb-1">{musician.name}</h2>
          <p className="text-black/50 mb-2">{musician.handle}</p>
          <p className="text-sm text-black/60">{musician.location}</p>
        </div>
      </div>

      {/* Bio */}
      {musician.bio && (
        <p className="text-black/80 mb-6 leading-relaxed">{musician.bio}</p>
      )}

      {/* Abilities */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-black/60 mb-3 uppercase tracking-wide">
          Abilities
        </h3>
        <div className="flex flex-wrap gap-2">
          {musician.abilities.map((ability) => (
            <span key={ability} className="chip">
              {ability}
            </span>
          ))}
        </div>
      </div>

      {/* Looking for */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-black/60 mb-3 uppercase tracking-wide">
          Looking for
        </h3>
        <div className="flex flex-wrap gap-2">
          {musician.lookingFor.map((role) => (
            <span key={role} className="chip bg-black text-white border-black">
              {role}
            </span>
          ))}
        </div>
      </div>

      {/* Portfolio */}
      {musician.portfolio && musician.portfolio.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-black/60 mb-3 uppercase tracking-wide">
            Portfolio
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {musician.portfolio.map((item, index) => (
              <div
                key={index}
                className="aspect-square bg-black/5 rounded-lg overflow-hidden relative group cursor-pointer"
              >
                {item.thumbnailUrl ? (
                  <img
                    src={item.thumbnailUrl}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <span className="text-xs text-black/40">{item.title}</span>
                  </div>
                )}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="text-white text-xs font-medium">{item.title}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center justify-center gap-6 pt-6 border-t border-black/10">
        <button
          onClick={onPass}
          className="w-16 h-16 rounded-full border-2 border-black/20 flex items-center justify-center hover:bg-black/5 hover:border-black/40 transition-all duration-200"
          aria-label="Pass"
        >
          <X size={28} className="text-black/60" />
        </button>
        <button
          onClick={onLike}
          className="w-16 h-16 rounded-full bg-black text-white flex items-center justify-center hover:bg-black/80 transition-all duration-200 shadow-lg"
          aria-label="Like"
        >
          <Heart size={28} />
        </button>
      </div>

      {/* Keyboard hint */}
      <p className="text-center text-xs text-black/40 mt-4">
        Use ← to pass, → to like
      </p>
    </div>
  );
}
