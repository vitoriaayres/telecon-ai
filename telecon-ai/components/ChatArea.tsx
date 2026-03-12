"use client";

import { useEffect, useRef } from "react";
import MessageBubble, { Message } from "./MessageBubble";
import { Sparkles, ArrowUpRight } from "lucide-react";

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

const SUGGESTIONS = [
  { label: "Analisar dados de telecom", prompt: "Quais KPI devo acompanhar em uma operação de telecom nacional?" },
  { label: "Otimizar rede", prompt: "Sugira um plano de melhoria de cobertura com foco em qualidade de sinal." },
  { label: "Relatório executivo", prompt: "Crie um resumo executivo semanal para liderança de operações." },
  { label: "Troubleshooting", prompt: "Monte um checklist para diagnóstico rápido de falhas em 5G." },
];

export default function ChatArea({ messages, isLoading }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 overflow-y-auto">
      {isEmpty ? (
        <WelcomeScreen />
      ) : (
        <div className="max-w-3xl mx-auto px-6 py-8 space-y-7">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {isLoading && (
            <div className="flex gap-3 items-start animate-fade-in">
              <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center flex-shrink-0">
                <Sparkles size={14} className="text-white" />
              </div>
              <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl">
                <span className="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}

function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 pb-12 animate-fade-in">
      <div className="inline-flex items-center gap-2 border border-border rounded-full px-3 py-1 text-xs text-text-secondary mb-6 bg-surface">
        <Sparkles size={12} className="text-text-primary" />
        TELECONTROL AI
      </div>

      <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-text-primary mb-2 text-center">
        Como posso ajudar?
      </h1>
      <p className="text-sm sm:text-base text-muted mb-10 text-center max-w-xl leading-relaxed">
        Assistente de IA para análises, operações e estratégia em telecom. Use uma das sugestões ou comece com sua pergunta.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
        {SUGGESTIONS.map((s) => (
          <SuggestionCard key={s.label} {...s} />
        ))}
      </div>
    </div>
  );
}

function SuggestionCard({
  label,
  prompt,
}: {
  label: string;
  prompt: string;
}) {
  return (
    <button className="flex items-start justify-between gap-4 bg-surface border border-border rounded-xl px-4 py-4 text-left hover:border-text-secondary/40 transition-all group">
      <div className="min-w-0">
        <p className="text-sm font-semibold text-text-primary transition-colors">
          {label}
        </p>
        <p className="text-xs text-muted mt-1 leading-relaxed line-clamp-2">
          {prompt}
        </p>
      </div>
      <ArrowUpRight size={15} className="text-muted group-hover:text-text-primary transition-colors flex-shrink-0 mt-0.5" />
    </button>
  );
}
