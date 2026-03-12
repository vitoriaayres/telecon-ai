"use client";

import { useRef, useEffect, useState } from "react";
import clsx from "clsx";
import {
  Send,
  Square,
  Paperclip,
  Mic,
  Globe,
  Zap,
  ChevronDown,
} from "lucide-react";

interface InputAreaProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  onStop: () => void;
  disabled?: boolean;
}

const MODELS = [
  { id: "telecon-pro", label: "TELECON Pro", description: "Mais avançado" },
  { id: "telecon-fast", label: "TELECON Fast", description: "Mais rápido" },
];

export default function InputArea({
  onSend,
  isLoading,
  onStop,
  disabled,
}: InputAreaProps) {
  const [value, setValue] = useState("");
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [showModels, setShowModels] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowModels(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSend = value.trim().length > 0 && !isLoading && !disabled;

  return (
    <div className="w-full max-w-3xl mx-auto px-6 pb-5 pt-2">
      {/* Model selector */}
      <div className="flex items-center gap-2 mb-2 relative" ref={dropdownRef}>
        <button
          onClick={() => setShowModels((v) => !v)}
          className="flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary transition-colors px-2 py-1 rounded-lg hover:bg-surface border border-transparent hover:border-border"
        >
          <Zap size={12} className="text-text-primary" />
          <span>{selectedModel.label}</span>
          <ChevronDown size={12} className={clsx("transition-transform", showModels && "rotate-180")} />
        </button>

        {showModels && (
          <div className="absolute bottom-full left-0 mb-1 w-56 bg-surface border border-border rounded-xl shadow-sm z-50 overflow-hidden animate-fade-in">
            {MODELS.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  setSelectedModel(model);
                  setShowModels(false);
                }}
                className={clsx(
                  "w-full flex items-start gap-2 px-3 py-2.5 text-left hover:bg-main transition-colors",
                  selectedModel.id === model.id && "bg-main"
                )}
              >
                <Zap size={14} className="text-text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-text-primary">{model.label}</p>
                  <p className="text-xs text-muted">{model.description}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Input box */}
      <div className="relative bg-surface rounded-2xl border border-border focus-within:border-text-primary/25 focus-within:shadow-[0_0_0_2px_rgba(17,17,17,0.06)] transition-all">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Me pergunte qualquer coisa..."
          rows={1}
          disabled={disabled}
          className="w-full bg-transparent text-text-primary placeholder:text-muted text-sm px-4 pt-3.5 pb-12 outline-none leading-relaxed max-h-[200px] overflow-y-auto block"
          style={{ resize: "none" }}
        />

        {/* Bottom bar */}
        <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-3 py-2.5">
          {/* Left actions */}
          <div className="flex items-center gap-1">
            <ActionButton icon={<Paperclip size={16} />} title="Anexar arquivo" />
            <ActionButton icon={<Globe size={16} />} title="Busca na web" />
            <ActionButton icon={<Mic size={16} />} title="Entrada de voz" />
          </div>

          {/* Send / Stop */}
          {isLoading ? (
            <button
              onClick={onStop}
              className="w-8 h-8 bg-text-primary rounded-full flex items-center justify-center hover:bg-accent-hover transition-colors flex-shrink-0"
              title="Parar geração"
            >
              <Square size={14} className="text-white fill-white" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canSend}
              className={clsx(
                "w-8 h-8 rounded-full flex items-center justify-center transition-all flex-shrink-0",
                canSend
                  ? "bg-text-primary hover:bg-accent-hover cursor-pointer"
                  : "bg-surface border border-border cursor-not-allowed opacity-50"
              )}
              title="Enviar mensagem"
            >
              <Send size={14} className="text-white" />
            </button>
          )}
        </div>
      </div>

      <p className="text-center text-xs text-muted/60 mt-2">
        TELECONTROL AI pode cometer erros. Considere verificar informações importantes.
      </p>
    </div>
  );
}

function ActionButton({
  icon,
  title,
}: {
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <button
      className="p-1.5 rounded-lg text-muted hover:text-text-secondary hover:bg-main transition-colors"
      title={title}
    >
      {icon}
    </button>
  );
}
