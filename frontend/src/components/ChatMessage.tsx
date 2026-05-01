import React from "react";
import ReactMarkdown from "react-markdown";
import { ReasoningBlock } from "./ReasoningBlock";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  reasoning?: string[];
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  reasoning,
}) => {
  const isUser = role === "user";

  return (
    <div
      className={`flex w-full mb-8 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="shrink-0 mr-4 mt-1">
          <div className="w-8 h-8 rounded-md bg-[#0A0A0A] border border-[#1A1A1A] flex items-center justify-center shadow-[0_0_10px_rgba(190,242,100,0.05)]">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 text-[#BEF264]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
        </div>
      )}

      <div className={`max-w-[85%] ${isUser ? "ml-auto" : ""}`}>
        {/* Render Reasoning ONLY for Assistant */}
        {!isUser && reasoning && <ReasoningBlock steps={reasoning} />}

        <div
          className={`px-5 py-4 text-[15px] leading-relaxed shadow-sm ${
            isUser
              ? "bg-[#0A0A0A] text-neutral-200 rounded-2xl rounded-tr-sm border border-[#1A1A1A]"
              : "bg-transparent text-neutral-300"
          }`}
        >
          <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-[#0A0A0A] prose-pre:border prose-pre:border-[#1A1A1A] prose-a:text-[#BEF264]">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};
