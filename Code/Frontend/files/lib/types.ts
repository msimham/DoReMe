export type FeedItem = {
  id: string;
  creatorName: string;
  handle: string;
  location?: string;
  title: string;
  description?: string;
  videoUrl?: string;
  thumbnailUrl?: string;
  tags?: string[];
};

export type Message = {
  id: string;
  from: "me" | "them";
  text: string;
  time: number;
};

export type Conversation = {
  id: string;
  musicianId: string;
  messages: Message[];
};

export type Project = {
  id: string;
  title: string;
  isPublic: boolean;
  stage: "Idea" | "Demo" | "Draft" | "Polished";
  video?: { name: string; url: string };
  notes?: string;
  lyrics?: string;
  updatedAt: number;
};

export type Ability = "writer" | "producer" | "composer" | "musician" | "singer";

export type Musician = {
  id: string;
  name: string;
  handle: string;
  location: string;
  abilities: Ability[];
  lookingFor: Ability[];
  bio?: string;
  portfolio?: { title: string; url?: string; thumbnailUrl?: string }[];
  avatarUrl?: string;
};

export type MatchState = {
  [musicianId: string]: "liked" | "passed";
};
