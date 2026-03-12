"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ThumbsUp, ThumbsDown, MessageSquare, Check, X } from "lucide-react";
import clsx from "clsx";

export type FeedbackValue = "positive" | "negative" | null;

interface FeedbackWidgetProps {
  /** ID único da análise (ex: rank + defeito) para rastrear qual resultado foi avaliado */
  resultId: string;
  /** Contexto exibido na confirmação */
  context?: string;
}

interface StoredFeedback {
  resultId: string;
  value: FeedbackValue;
  comment: string;
  timestamp: number;
}

function saveFeedback(item: StoredFeedback) {
  try {
    const raw = localStorage.getItem("telecontrol_feedback");
    const list: StoredFeedback[] = raw ? JSON.parse(raw) : [];
    // Substitui se já existe feedback para este resultId
    const filtered = list.filter((f) => f.resultId !== item.resultId);
    filtered.push(item);
    localStorage.setItem("telecontrol_feedback", JSON.stringify(filtered));
  } catch {
    // silencioso — localStorage pode estar indisponível
  }
}

function loadFeedback(resultId: string): StoredFeedback | null {
  try {
    const raw = localStorage.getItem("telecontrol_feedback");
    if (!raw) return null;
    const list: StoredFeedback[] = JSON.parse(raw);
    return list.find((f) => f.resultId === resultId) ?? null;
  } catch {
    return null;
  }
}

export default function FeedbackWidget({ resultId, context }: FeedbackWidgetProps) {
  const existing = loadFeedback(resultId);

  const [vote, setVote] = useState<FeedbackValue>(existing?.value ?? null);
  const [showComment, setShowComment] = useState(false);
  const [comment, setComment] = useState(existing?.comment ?? "");
  const [submitted, setSubmitted] = useState(!!existing);
  const [saving, setSaving] = useState(false);

  function handleVote(v: "positive" | "negative") {
    if (submitted) return;
    setVote(v);
    if (v === "negative") {
      setShowComment(true);
    } else {
      commit(v, "");
    }
  }

  async function commit(v: FeedbackValue, c: string) {
    setSaving(true);
    // Salva localmente + dispara para a API (best-effort)
    const payload: StoredFeedback = {
      resultId,
      value: v,
      comment: c.trim(),
      timestamp: Date.now(),
    };
    saveFeedback(payload);

    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...payload, context }),
      });
    } catch {
      // silencioso — persiste localmente de qualquer forma
    }

    setSaving(false);
    setSubmitted(true);
    setShowComment(false);
  }

  function handleSubmitComment(e: React.FormEvent) {
    e.preventDefault();
    commit(vote, comment);
  }

  function handleReset() {
    setVote(null);
    setComment("");
    setSubmitted(false);
    setShowComment(false);
    try {
      const raw = localStorage.getItem("telecontrol_feedback");
      if (raw) {
        const list: StoredFeedback[] = JSON.parse(raw);
        localStorage.setItem(
          "telecontrol_feedback",
          JSON.stringify(list.filter((f) => f.resultId !== resultId))
        );
      }
    } catch {
      // silencioso
    }
  }

  return (
    <div className="mt-3 pt-3 border-t border-border">
      <AnimatePresence mode="wait">
        {submitted ? (
          /* ── Estado confirmado ── */
          <motion.div
            key="done"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.25 }}
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-2 text-xs text-muted">
              <span
                className={clsx(
                  "flex items-center justify-center w-5 h-5 rounded-full",
                  vote === "positive"
                    ? "bg-emerald-500/15 text-emerald-500"
                    : "bg-red-500/15 text-red-500"
                )}
              >
                <Check size={10} />
              </span>
              <span>
                {vote === "positive"
                  ? "Diagnóstico útil! Obrigado."
                  : "Feedback registrado. Vamos melhorar."}
              </span>
            </div>
            <button
              onClick={handleReset}
              className="text-xs text-muted hover:text-text-secondary transition-colors"
            >
              Refazer
            </button>
          </motion.div>
        ) : (
          /* ── Estado inicial / votação ── */
          <motion.div
            key="voting"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.25 }}
            className="space-y-2.5"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted">Este diagnóstico foi útil?</p>

              <div className="flex items-center gap-1.5">
                {/* Thumbs Up */}
                <motion.button
                  type="button"
                  whileTap={{ scale: 0.88 }}
                  onClick={() => handleVote("positive")}
                  disabled={saving}
                  title="Sim, foi útil"
                  className={clsx(
                    "flex items-center gap-1 px-2.5 py-1 rounded-lg border text-xs transition-all duration-200",
                    vote === "positive"
                      ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-500"
                      : "border-border text-muted hover:border-emerald-500/40 hover:text-emerald-500 hover:bg-emerald-500/8"
                  )}
                >
                  <ThumbsUp size={12} />
                  <span>Sim</span>
                </motion.button>

                {/* Thumbs Down */}
                <motion.button
                  type="button"
                  whileTap={{ scale: 0.88 }}
                  onClick={() => handleVote("negative")}
                  disabled={saving}
                  title="Não foi útil"
                  className={clsx(
                    "flex items-center gap-1 px-2.5 py-1 rounded-lg border text-xs transition-all duration-200",
                    vote === "negative"
                      ? "border-red-500/50 bg-red-500/10 text-red-500"
                      : "border-border text-muted hover:border-red-500/40 hover:text-red-500 hover:bg-red-500/8"
                  )}
                >
                  <ThumbsDown size={12} />
                  <span>Não</span>
                </motion.button>
              </div>
            </div>

            {/* Caixa de comentário — só aparece no thumbs down */}
            <AnimatePresence>
              {showComment && (
                <motion.form
                  key="comment"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.22, ease: "easeOut" }}
                  onSubmit={handleSubmitComment}
                  className="overflow-hidden"
                >
                  <div className="pt-1 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs text-text-secondary">
                      <MessageSquare size={11} className="text-muted" />
                      O que poderia ser diferente? (opcional)
                    </div>
                    <textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Ex: O diagnóstico não corresponde ao sintoma descrito..."
                      rows={2}
                      maxLength={300}
                      className="w-full px-3 py-2 rounded-xl border border-border bg-main text-sm text-text-primary
                        placeholder:text-muted resize-none
                        focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent/40
                        transition-all duration-200"
                    />
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs text-muted">{comment.length}/300</span>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setShowComment(false);
                            setVote(null);
                          }}
                          className="flex items-center gap-1 text-xs text-muted hover:text-text-secondary transition-colors px-2 py-1"
                        >
                          <X size={11} />
                          Cancelar
                        </button>
                        <button
                          type="submit"
                          disabled={saving}
                          className="flex items-center gap-1.5 text-xs bg-accent text-main px-3 py-1.5 rounded-lg
                            hover:bg-accent-hover disabled:opacity-50 transition-all duration-200"
                        >
                          {saving ? (
                            <motion.span
                              animate={{ rotate: 360 }}
                              transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                              className="w-3 h-3 border-2 border-main/30 border-t-main rounded-full inline-block"
                            />
                          ) : (
                            <Check size={11} />
                          )}
                          Enviar
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.form>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
