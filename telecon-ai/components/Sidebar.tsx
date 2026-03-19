"use client";

import { useState } from "react";
import clsx from "clsx";
import {
  MessageSquarePlus,
  Search,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "@/components/ui/theme-provider";

export interface Conversation {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
}

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  collapsed,
  onToggle,
}: SidebarProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const { theme, toggleTheme } = useTheme();

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const grouped = groupByDate(filtered);

  return (
    <aside
      className={clsx(
        "flex flex-col h-full bg-sidebar border-r border-border transition-all duration-300 ease-in-out relative",
        collapsed ? "w-14" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <img src="/logo.svg" alt="Break FIX" className="logo-telecontrol w-7 h-7 flex-shrink-0" />
            <span className="font-semibold text-sm text-text-primary tracking-tight">
              Break FIX
            </span>
          </div>
        )}
        {collapsed && (
          <img src="/logo.svg" alt="Break FIX" className="logo-telecontrol w-7 h-7 mx-auto" />
        )}
      </div>

      {/* New chat button */}
      <div className={clsx("px-2 py-2", collapsed && "flex justify-center")}>
        <button
          onClick={onNew}
          className={clsx(
            "flex items-center gap-2 rounded-lg transition-colors text-sm font-medium border border-border",
            "text-text-secondary hover:text-text-primary hover:bg-surface",
            collapsed
              ? "p-2 justify-center w-10 h-10"
              : "px-3 py-2 w-full"
          )}
          title="Nova análise"
        >
          <MessageSquarePlus size={17} className="flex-shrink-0" />
          {!collapsed && <span>Nova análise</span>}
        </button>
      </div>

      {/* Search */}
      {!collapsed && (
        <div className="px-2 pb-2">
          <div className="relative">
            <Search
              size={14}
              className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted"
            />
            <input
              type="text"
              placeholder="Pesquisar..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-surface text-text-secondary placeholder:text-muted text-sm rounded-lg pl-8 pr-3 py-2 outline-none focus:ring-1 focus:ring-accent/20 border border-border transition-all"
            />
          </div>
        </div>
      )}

      {/* Conversations list */}
      <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-4">
        {!collapsed &&
          Object.entries(grouped).map(([label, convs]) => (
            <div key={label}>
              <p className="text-xs text-muted font-medium px-2 py-1">
                {label}
              </p>
              <div className="space-y-0.5">
                {convs.map((conv) => (
                  <ConversationItem
                    key={conv.id}
                    conv={conv}
                    isActive={conv.id === activeId}
                    isHovered={hoveredId === conv.id}
                    onHover={setHoveredId}
                    onSelect={onSelect}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            </div>
          ))}
      </div>

      {/* Footer: dark mode toggle */}
      <div className={clsx(
        "flex-shrink-0 border-t border-border px-2 py-2",
        collapsed ? "flex justify-center" : "flex items-center justify-between"
      )}>
        <button
          onClick={toggleTheme}
          className={clsx(
            "flex items-center gap-2 rounded-lg transition-colors text-sm font-medium border border-border",
            "text-text-secondary hover:text-text-primary hover:bg-surface",
            collapsed ? "p-2 w-10 h-10 justify-center" : "px-3 py-2 flex-1"
          )}
          title={theme === "dark" ? "Modo claro" : "Modo escuro"}
        >
          {theme === "dark" ? (
            <Sun size={15} className="flex-shrink-0" />
          ) : (
            <Moon size={15} className="flex-shrink-0" />
          )}
          {!collapsed && (
            <span>{theme === "dark" ? "Modo claro" : "Modo escuro"}</span>
          )}
        </button>
      </div>

      {/* Toggle button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-surface border border-border rounded-full flex items-center justify-center text-muted hover:text-text-primary hover:bg-main transition-all z-10"
        title={collapsed ? "Expandir sidebar" : "Recolher sidebar"}
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </aside>
  );
}

function ConversationItem({
  conv,
  isActive,
  isHovered,
  onHover,
  onSelect,
  onDelete,
}: {
  conv: Conversation;
  isActive: boolean;
  isHovered: boolean;
  onHover: (id: string | null) => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div
      className={clsx(
        "group relative flex items-center rounded-lg px-2 py-2 cursor-pointer transition-colors",
        isActive
          ? "bg-surface text-text-primary border border-border"
          : "text-text-secondary hover:bg-surface hover:text-text-primary"
      )}
      onClick={() => onSelect(conv.id)}
      onMouseEnter={() => onHover(conv.id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate leading-tight">{conv.title}</p>
        <p className="text-xs text-muted truncate mt-0.5">{conv.preview}</p>
      </div>

      {(isActive || isHovered) && (
        <div className="flex items-center gap-0.5 ml-1 flex-shrink-0">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conv.id);
            }}
            className="p-1 rounded-md text-muted hover:text-red-400 hover:bg-red-400/10 transition-colors"
            title="Excluir"
          >
            <Trash2 size={13} />
          </button>
        </div>
      )}
    </div>
  );
}

function groupByDate(convs: Conversation[]): Record<string, Conversation[]> {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const sevenDaysAgo = new Date(today);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const groups: Record<string, Conversation[]> = {};

  convs.forEach((c) => {
    const d = new Date(c.timestamp);
    let label: string;

    if (d >= today) {
      label = "Hoje";
    } else if (d >= yesterday) {
      label = "Ontem";
    } else if (d >= sevenDaysAgo) {
      label = "Últimos 7 dias";
    } else {
      label = "Mais antigos";
    }

    if (!groups[label]) groups[label] = [];
    groups[label].push(c);
  });

  return groups;
}
