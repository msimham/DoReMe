"use client";

import { Project } from "@/lib/types";
import { Upload, FileText, Music } from "lucide-react";
import { useState, useRef } from "react";

interface ProfileProjectCardProps {
  project: Project;
  onUpdate: (updates: Partial<Project>) => void;
}

export default function ProfileProjectCard({ project, onUpdate }: ProfileProjectCardProps) {
  const [notes, setNotes] = useState(project.notes || "");
  const [lyrics, setLyrics] = useState(project.lyrics || "");
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      onUpdate({ video: { name: file.name, url } });
    }
  };

  const handleSave = () => {
    onUpdate({ notes, lyrics });
    alert("Project saved!");
  };

  return (
    <div className="card p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-lg">{project.title}</h3>
        <select
          value={project.stage}
          onChange={(e) => onUpdate({ stage: e.target.value as Project["stage"] })}
          className="text-xs px-3 py-1 border border-black/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-black/20"
        >
          <option value="Idea">Idea</option>
          <option value="Demo">Demo</option>
          <option value="Draft">Draft</option>
          <option value="Polished">Polished</option>
        </select>
      </div>

      {/* Video upload */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Video</label>
        {project.video ? (
          <div className="relative aspect-video bg-black/5 rounded-lg overflow-hidden">
            <video
              src={project.video.url}
              controls
              className="w-full h-full object-cover"
            />
            <button
              onClick={() => onUpdate({ video: undefined })}
              className="absolute top-2 right-2 bg-white/90 px-3 py-1 rounded-lg text-xs font-medium hover:bg-white transition-colors"
            >
              Remove
            </button>
          </div>
        ) : (
          <button
            onClick={() => videoInputRef.current?.click()}
            className="w-full aspect-video border-2 border-dashed border-black/20 rounded-lg flex flex-col items-center justify-center gap-2 hover:bg-black/5 transition-colors"
          >
            <Upload size={24} className="text-black/40" />
            <span className="text-sm text-black/60">Upload video</span>
          </button>
        )}
        <input
          ref={videoInputRef}
          type="file"
          accept="video/*"
          onChange={handleVideoUpload}
          className="hidden"
        />
      </div>

      {/* Notes */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2 flex items-center gap-2">
          <FileText size={16} />
          Notes
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add production notes, ideas, feedback..."
          className="input resize-none h-24"
        />
      </div>

      {/* Lyrics */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2 flex items-center gap-2">
          <Music size={16} />
          Lyrics
        </label>
        <textarea
          value={lyrics}
          onChange={(e) => setLyrics(e.target.value)}
          placeholder="Write your lyrics here..."
          className="input resize-none h-32"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-black/5">
        <span className="text-xs text-black/40">
          {project.isPublic ? "Public" : "Private"}
        </span>
        <button onClick={handleSave} className="btn-primary text-sm">
          Save Changes
        </button>
      </div>
    </div>
  );
}
