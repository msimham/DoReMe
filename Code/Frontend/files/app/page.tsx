"use client";

import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import FeedCard from "@/components/FeedCard";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import { FeedItem } from "@/lib/types";
import { searchVideos } from "@/lib/serpApiClient";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeed("");
  }, []);

  const loadFeed = async (searchQuery: string) => {
    setLoading(true);
    const results = await searchVideos(searchQuery);
    setFeedItems(results);
    setLoading(false);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadFeed(query);
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-6">Home Feed</h1>
          
          {/* Search bar */}
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-black/40" size={20} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search videos (artist, song, genre)"
              className="input pl-12 w-full"
            />
          </form>
        </div>

        {/* Feed */}
        <div className="space-y-6">
          {loading ? (
            <>
              <LoadingSkeleton />
              <LoadingSkeleton />
              <LoadingSkeleton />
            </>
          ) : feedItems.length > 0 ? (
            feedItems.map((item) => <FeedCard key={item.id} item={item} />)
          ) : (
            <div className="text-center py-20">
              <p className="text-black/40 text-lg">No results found</p>
              <p className="text-black/30 text-sm mt-2">Try a different search term</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
