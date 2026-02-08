import { Conversation, Project, MatchState } from "./types";

const STORAGE_KEYS = {
  CONVERSATIONS: "doreme_conversations",
  PROJECTS: "doreme_projects",
  MATCHES: "doreme_matches",
  ONBOARDED: "doreme_onboarded",
} as const;

// Conversations
export const getConversations = (): Conversation[] => {
  if (typeof window === "undefined") return [];
  const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
  return data ? JSON.parse(data) : [];
};

export const saveConversations = (conversations: Conversation[]) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
};

export const addMessage = (conversationId: string, message: any) => {
  const conversations = getConversations();
  const convIndex = conversations.findIndex((c) => c.id === conversationId);
  
  if (convIndex >= 0) {
    conversations[convIndex].messages.push(message);
  } else {
    conversations.push({
      id: conversationId,
      musicianId: conversationId.replace("conv-", ""),
      messages: [message],
    });
  }
  
  saveConversations(conversations);
};

// Projects
export const getProjects = (): Project[] => {
  if (typeof window === "undefined") return [];
  const data = localStorage.getItem(STORAGE_KEYS.PROJECTS);
  return data ? JSON.parse(data) : [];
};

export const saveProjects = (projects: Project[]) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEYS.PROJECTS, JSON.stringify(projects));
};

export const updateProject = (projectId: string, updates: Partial<Project>) => {
  const projects = getProjects();
  const index = projects.findIndex((p) => p.id === projectId);
  
  if (index >= 0) {
    projects[index] = { ...projects[index], ...updates, updatedAt: Date.now() };
    saveProjects(projects);
  }
};

// Match state
export const getMatchState = (): MatchState => {
  if (typeof window === "undefined") return {};
  const data = localStorage.getItem(STORAGE_KEYS.MATCHES);
  return data ? JSON.parse(data) : {};
};

export const saveMatchState = (state: MatchState) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEYS.MATCHES, JSON.stringify(state));
};

export const updateMatchState = (musicianId: string, action: "liked" | "passed") => {
  const state = getMatchState();
  state[musicianId] = action;
  saveMatchState(state);
};

// Onboarding
export const hasOnboarded = (): boolean => {
  if (typeof window === "undefined") return true;
  return localStorage.getItem(STORAGE_KEYS.ONBOARDED) === "true";
};

export const setOnboarded = () => {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEYS.ONBOARDED, "true");
};
