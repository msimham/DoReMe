"use client";

import { Conversation, Message } from "@/lib/types";
import { Send } from "lucide-react";
import { useState, useEffect, useRef } from "react";

interface DMThreadProps {
  conversation: Conversation;
  musicianName: string;
  onSendMessage: (text: string) => void;
}

export default function DMThread({ conversation, musicianName, onSendMessage }: DMThreadProps) {
  const [message, setMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation.messages]);

  const handleSend = () => {
    if (!message.trim()) return;

    onSendMessage(message);
    setMessage("");

    // Simulate typing indicator and auto-reply
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const replies = [
        "That sounds great!",
        "I'm interested! Tell me more.",
        "Let me check my schedule and get back to you.",
        "Love the idea. When can we start?",
        "I'll send over some samples soon.",
      ];
      const randomReply = replies[Math.floor(Math.random() * replies.length)];
      onSendMessage(randomReply, "them");
    }, 1500);
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-black/10 flex-shrink-0">
        <h2 className="font-bold text-xl">{musicianName}</h2>
        <p className="text-sm text-black/50">Active now</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {conversation.messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.from === "me" ? "justify-end" : "justify-start"} animate-fade-in`}
          >
            <div
              className={`max-w-md px-4 py-3 rounded-2xl ${
                msg.from === "me"
                  ? "bg-black text-white"
                  : "bg-black/5 text-black"
              }`}
            >
              <p className="text-sm leading-relaxed">{msg.text}</p>
              <p
                className={`text-xs mt-1 ${
                  msg.from === "me" ? "text-white/60" : "text-black/40"
                }`}
              >
                {formatTime(msg.time)}
              </p>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-black/5 px-4 py-3 rounded-2xl">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-black/10 flex-shrink-0">
        <div className="flex gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message..."
            className="input flex-1"
          />
          <button
            onClick={handleSend}
            disabled={!message.trim()}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
