"use client";

import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Sparkles, Copy, ThumbsUp, ThumbsDown, RotateCcw, Check } from "lucide-react";
import { useState, useEffect } from "react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<"up" | "down" | null>(null);
  const [displayedContent, setDisplayedContent] = useState(
    message.isStreaming ? "" : message.content
  );

  // Streaming effect
  useEffect(() => {
    if (!message.isStreaming) {
      setDisplayedContent(message.content);
      return;
    }

    setDisplayedContent("");
    let i = 0;
    const interval = setInterval(() => {
      if (i < message.content.length) {
        setDisplayedContent(message.content.slice(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 8);

    return () => clearInterval(interval);
  }, [message.content, message.isStreaming]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={clsx(
        "group flex gap-3 w-full animate-slide-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Avatar — assistant */}
      {!isUser && (
        <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center flex-shrink-0 mt-0.5">
          <Sparkles size={14} className="text-white" />
        </div>
      )}

      {/* Bubble */}
      <div className={clsx("flex flex-col max-w-[85%]", isUser && "items-end")}>
        <div
          className={clsx(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-surface border border-border text-text-primary rounded-br-md"
              : "text-text-primary"
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{displayedContent}</p>
          ) : (
            <div className="prose-chat">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {displayedContent}
              </ReactMarkdown>
              {message.isStreaming && displayedContent.length < message.content.length && (
                <span className="inline-block w-0.5 h-4 bg-text-primary ml-0.5 animate-blink" />
              )}
            </div>
          )}
        </div>

        {/* Actions — assistant only */}
        {!isUser && (
          <div className="flex items-center gap-1 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <ActionBtn
              icon={copied ? <Check size={13} /> : <Copy size={13} />}
              onClick={handleCopy}
              active={copied}
              title="Copiar"
            />
            <ActionBtn
              icon={<ThumbsUp size={13} />}
              onClick={() => setLiked(liked === "up" ? null : "up")}
              active={liked === "up"}
              title="Curtir"
            />
            <ActionBtn
              icon={<ThumbsDown size={13} />}
              onClick={() => setLiked(liked === "down" ? null : "down")}
              active={liked === "down"}
              title="Não curtir"
            />
            <ActionBtn
              icon={<RotateCcw size={13} />}
              onClick={() => {}}
              title="Regenerar"
            />
          </div>
        )}
      </div>

      {/* Avatar — user */}
      {isUser && (
        <div className="w-8 h-8 rounded-md bg-surface border border-border flex items-center justify-center flex-shrink-0 mt-0.5">
          <User size={14} className="text-text-secondary" />
        </div>
      )}
    </div>
  );
}

function ActionBtn({
  icon,
  onClick,
  active,
  title,
}: {
  icon: React.ReactNode;
  onClick: () => void;
  active?: boolean;
  title: string;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={clsx(
        "p-1.5 rounded-lg transition-colors",
        active
          ? "text-accent bg-accent/10"
          : "text-muted hover:text-text-secondary hover:bg-surface"
      )}
    >
      {icon}
    </button>
  );
}
