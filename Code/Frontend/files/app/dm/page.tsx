"use client";

import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import DMThread from "@/components/DMThread";
import { Conversation, Message } from "@/lib/types";
import { getConversations, saveConversations, addMessage } from "@/lib/storage";
import { mockConversations, mockMusicians } from "@/lib/mockData";

export default function DMPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [showNewConvModal, setShowNewConvModal] = useState(false);

  useEffect(() => {
    const stored = getConversations();
    if (stored.length === 0) {
      // Initialize with mock data
      saveConversations(mockConversations);
      setConversations(mockConversations);
      setSelectedConvId(mockConversations[0]?.id || null);
    } else {
      setConversations(stored);
      setSelectedConvId(stored[0]?.id || null);
    }
  }, []);

  const selectedConv = conversations.find((c) => c.id === selectedConvId);
  const musician = selectedConv
    ? mockMusicians.find((m) => m.id === selectedConv.musicianId)
    : null;

  const handleSendMessage = (text: string, from: "me" | "them" = "me") => {
    if (!selectedConvId) return;

    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      from,
      text,
      time: Date.now(),
    };

    addMessage(selectedConvId, newMessage);

    // Update local state
    setConversations((prev) =>
      prev.map((c) =>
        c.id === selectedConvId
          ? { ...c, messages: [...c.messages, newMessage] }
          : c
      )
    );
  };

  const handleNewConversation = (musicianId: string) => {
    const newConv: Conversation = {
      id: `conv-${musicianId}`,
      musicianId,
      messages: [],
    };

    const updated = [...conversations, newConv];
    setConversations(updated);
    saveConversations(updated);
    setSelectedConvId(newConv.id);
    setShowNewConvModal(false);
  };

  return (
    <div className="h-screen flex">
      {/* Conversations list */}
      <div className="w-80 border-r border-black/10 flex flex-col">
        <div className="p-6 border-b border-black/10 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Messages</h1>
          <button
            onClick={() => setShowNewConvModal(true)}
            className="w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:bg-black/80 transition-colors"
          >
            <Plus size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-6 text-center text-black/40">
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new one!</p>
            </div>
          ) : (
            conversations.map((conv) => {
              const m = mockMusicians.find((mu) => mu.id === conv.musicianId);
              if (!m) return null;

              const lastMessage = conv.messages[conv.messages.length - 1];
              const isSelected = selectedConvId === conv.id;

              return (
                <button
                  key={conv.id}
                  onClick={() => setSelectedConvId(conv.id)}
                  className={`w-full p-4 text-left border-b border-black/5 hover:bg-black/5 transition-colors ${
                    isSelected ? "bg-black/5" : ""
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 bg-black/5 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-medium">{m.name[0]}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm truncate">{m.name}</h3>
                      {lastMessage && (
                        <p className="text-xs text-black/50 truncate mt-1">
                          {lastMessage.text}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Thread */}
      <div className="flex-1">
        {selectedConv && musician ? (
          <DMThread
            conversation={selectedConv}
            musicianName={musician.name}
            onSendMessage={handleSendMessage}
          />
        ) : (
          <div className="h-full flex items-center justify-center text-black/40">
            <p>Select a conversation to start messaging</p>
          </div>
        )}
      </div>

      {/* New conversation modal */}
      {showNewConvModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 animate-scale-in">
            <h2 className="text-2xl font-bold mb-6">Start New Conversation</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto mb-6">
              {mockMusicians.map((m) => (
                <button
                  key={m.id}
                  onClick={() => handleNewConversation(m.id)}
                  className="w-full p-4 rounded-lg border border-black/10 hover:bg-black/5 transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-black/5 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium">{m.name[0]}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm">{m.name}</h3>
                      <p className="text-xs text-black/50">{m.handle}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowNewConvModal(false)}
              className="btn-secondary w-full"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
