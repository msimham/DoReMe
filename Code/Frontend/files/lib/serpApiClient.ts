import { FeedItem } from "./types";
import { mockFeedItems } from "./mockData";

const SERPAPI_KEY = process.env.NEXT_PUBLIC_SERPAPI_KEY;

export async function searchVideos(query: string): Promise<FeedItem[]> {
  // If no API key, return mock data
  if (!SERPAPI_KEY) {
    console.log("No SerpAPI key found, using mock data");
    await new Promise((resolve) => setTimeout(resolve, 800)); // Simulate network delay
    
    if (!query) return mockFeedItems;
    
    // Simple filter on mock data
    const lowerQuery = query.toLowerCase();
    return mockFeedItems.filter(
      (item) =>
        item.title.toLowerCase().includes(lowerQuery) ||
        item.description?.toLowerCase().includes(lowerQuery) ||
        item.tags?.some((tag) => tag.toLowerCase().includes(lowerQuery))
    );
  }

  // Real SerpAPI implementation
  try {
    const params = new URLSearchParams({
      engine: "youtube",
      search_query: query,
      api_key: SERPAPI_KEY,
    });

    const response = await fetch(`https://serpapi.com/search?${params}`);
    
    if (!response.ok) {
      throw new Error("SerpAPI request failed");
    }

    const data = await response.json();
    
    // Transform SerpAPI response to FeedItem format
    const videos = data.video_results || [];
    return videos.slice(0, 10).map((video: any, index: number) => ({
      id: `serp-${index}`,
      creatorName: video.channel?.name || "Unknown Creator",
      handle: `@${video.channel?.name?.toLowerCase().replace(/\s+/g, "") || "unknown"}`,
      location: undefined,
      title: video.title || "Untitled",
      description: video.description || "",
      videoUrl: video.link,
      thumbnailUrl: video.thumbnail,
      tags: [],
    }));
  } catch (error) {
    console.error("SerpAPI error, falling back to mock data:", error);
    return mockFeedItems;
  }
}
