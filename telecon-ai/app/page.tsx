"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import FilterForm, { FilterValues } from "@/components/FilterForm";
import ResultsPanel, { AnalysisOutput } from "@/components/ResultsPanel";
import { Sparkles, ArrowLeft, LogOut } from "lucide-react";
import AnimatedGradientBackground from "@/components/ui/animated-gradient-background";
import { useTheme } from "@/components/ui/theme-provider";
import { Typewriter } from "@/components/ui/typewriter";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, X } from "lucide-react";

// Chama a API real do backend FastAPI
async function fetchClassification(
  filters: FilterValues
): Promise<AnalysisOutput> {
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      texto_cliente: filters.defeitoReclamado,
      tipo_produto: filters.tipoProduto || null,
      segmento: filters.segmento || null,
      regiao: filters.regiao || null,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ?? `Erro ${response.status}`);
  }

  const data = await response.json();

  // Mapeia a resposta da API para o formato AnalysisOutput esperado pelo ResultsPanel
  const maxConfianca: number = data.resultados[0]?.confianca_pct ?? 1;

  const results: AnalysisOutput["results"] = data.resultados.map(
    (r: {
      rank: number;
      defeito_sugerido: string;
      confianca_pct: number;
      documentacao: string;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      descricao_llm?: any;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      acao_recomendada_llm?: any;
    }) => {
      const descricao = typeof r.descricao_llm === "string" ? r.descricao_llm.trim() : "";
      const acao = typeof r.acao_recomendada_llm === "string" ? r.acao_recomendada_llm.trim() : "";

      return {
        rank: r.rank,
        defect: r.defeito_sugerido,
        // Confiança relativa: rank 1 = 100%, demais proporcionais ao rank 1
        confidenceRel: maxConfianca > 0 ? Math.round((r.confianca_pct / maxConfianca) * 100) : 0,
        confidenceAbs: r.confianca_pct,
        description: descricao || "Análise baseada no histórico de ordens de serviço.",
        recommendedAction: acao || "Consultar manual técnico do componente.",
        manualUrl: r.documentacao || "",
      };
    }
  );

  const modelLabel =
    data.modelo_ativo === "semantico"
      ? `Semântico (MiniLM) · ${data.total_classes ?? "?"} classes`
      : `RandomForest · ${data.total_classes ?? "?"} classes`;

  return {
    filters,
    results,
    totalAnalyzed: data.total_registros ?? data.total_classes ?? 0,
    modelUsed: modelLabel,
  };
}


function generateId() {
  return Math.random().toString(36).slice(2, 11);
}

interface AnalysisRecord {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  output: AnalysisOutput;
}

interface AuthData {
  email: string;
  setor: string;
  setorDesc: string;
}

export default function ClassifierPage() {
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);
  const [authData, setAuthData] = useState<AuthData | null>(null);
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();

  // Verifica autenticação ao montar o componente
  useEffect(() => {
    const raw = localStorage.getItem("telecontrol_auth");
    if (!raw) {
      router.replace("/login");
      return;
    }
    try {
      const data = JSON.parse(raw) as AuthData;
      setAuthData(data);
    } catch {
      localStorage.removeItem("telecontrol_auth");
      router.replace("/login");
      return;
    }
    setAuthChecked(true);
  }, [router]);

  function handleLogout() {
    localStorage.removeItem("telecontrol_auth");
    router.replace("/login");
  }

  const activeRecord = history.find((h) => h.id === activeId) ?? null;

  const handleAnalyze = useCallback(
    async (filters: FilterValues) => {
      setIsLoading(true);
      setError(null);
      try {
        const output = await fetchClassification(filters);
        const id = generateId();
        const record: AnalysisRecord = {
          id,
          title:
            filters.defeitoReclamado.slice(0, 45) +
            (filters.defeitoReclamado.length > 45 ? "..." : ""),
          preview:
            filters.tipoProduto +
            (filters.segmento ? ` · ${filters.segmento}` : ""),
          timestamp: new Date(),
          output,
        };
        setHistory((prev) => [record, ...prev]);
        setActiveId(id);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Erro desconhecido";
        setError(message);
        console.error("Erro na análise:", err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const handleNew = useCallback(() => setActiveId(null), []);

  const handleDelete = useCallback((id: string) => {
    setHistory((prev) => prev.filter((h) => h.id !== id));
    setActiveId((curr) => (curr === id ? null : curr));
  }, []);

  const conversations = history.map((h) => ({
    id: h.id,
    title: h.title,
    preview: h.preview,
    timestamp: h.timestamp,
  }));

  // Tela de carregamento enquanto verifica auth
  if (!authChecked) {
    return (
      <div className="relative flex items-center justify-center min-h-screen overflow-hidden bg-main">
        <AnimatedGradientBackground
          Breathing
          animationSpeed={0.012}
          breathingRange={7}
          startingGap={140}
          topOffset={5}
          gradientColors={
            theme === "dark"
              ? ["#0f0f16", "#131328", "#181836", "#12122a", "#0d0d1e", "#0b0b16", "#0f0f16"]
              : ["#fcfcfa", "#e8f0fe", "#ddd6fe", "#c7d2fe", "#bfdbfe", "#e0f2fe", "#f8fafc"]
          }
          gradientStops={[25, 42, 55, 65, 75, 87, 100]}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 flex flex-col items-center gap-4"
        >
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-border border-t-accent rounded-full inline-block"
          />
          <p className="text-xs text-muted">Carregando...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-main">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={handleNew}
        onDelete={handleDelete}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((v) => !v)}
      />

      <main className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Header */}
        <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-border bg-main/80 backdrop-blur-sm">
          <h2 className="text-sm font-semibold text-text-primary tracking-tight">
            {activeRecord ? activeRecord.title : "Nova classificação"}
          </h2>
          <div className="flex items-center gap-2.5">
            {authData && (
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="hidden sm:flex items-center gap-2"
                >
                  <span className="text-xs text-muted bg-surface px-2.5 py-1 rounded-full border border-border">
                    {authData.setor}
                  </span>
                  <span className="text-xs text-muted">{authData.email}</span>
                </motion.div>
              </AnimatePresence>
            )}
            <span className="text-xs text-muted bg-surface px-2.5 py-1 rounded-full border border-border">
              Preview
            </span>
            <button
              onClick={handleLogout}
              title="Sair"
              className="flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary bg-surface px-2.5 py-1 rounded-full border border-border transition-colors"
            >
              <LogOut size={12} />
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        </header>
Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="fixed top-4 right-4 z-50 flex items-start gap-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl p-4 max-w-sm"
            >
              <AlertCircle size={16} className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-700 dark:text-red-300 font-medium">Erro</p>
                <p className="text-xs text-red-600 dark:text-red-400 mt-0.5">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-200 flex-shrink-0"
              >
                <X size={14} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 
        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {activeRecord ? (
            /* ── Resultado: formulário compacto à esquerda + resultados à direita ── */
            <div className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-8 items-start">
              {/* Formulário compacto */}
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={handleNew}
                  className="flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary transition-colors"
                >
                  <ArrowLeft size={13} />
                  Nova classificação
                </button>
                <div className="bg-surface border border-border rounded-2xl p-5">
                  <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-4">
                    Filtros
                  </p>
                  <FilterForm
                    onAnalyze={handleAnalyze}
                    isLoading={isLoading}
                    compact
                  />
                </div>
              </div>

              {/* Resultados */}
              <ResultsPanel output={activeRecord.output} />
            </div>
          ) : (
            /* ── Tela inicial: formulário centralizado ── */
            <div className="relative flex flex-col items-center justify-center h-full px-6 pb-10 animate-fade-in">
              <AnimatedGradientBackground
                Breathing
                animationSpeed={0.015}
                breathingRange={6}
                startingGap={130}
                topOffset={10}
                gradientColors={
                  theme === "dark"
                    ? [
                        "#0f0f16",
                        "#131328",
                        "#181836",
                        "#12122a",
                        "#0d0d1e",
                        "#0b0b16",
                        "#0f0f16",
                      ]
                    : [
                        "#fcfcfa",
                        "#e8f0fe",
                        "#ddd6fe",
                        "#c7d2fe",
                        "#bfdbfe",
                        "#e0f2fe",
                        "#f8fafc",
                      ]
                }
                gradientStops={[25, 42, 55, 65, 75, 87, 100]}
              />
              <div className="relative z-10 w-full max-w-2xl">
                <div className="inline-flex items-center gap-2 border border-border rounded-full px-3 py-1 text-xs text-text-secondary mb-6 bg-surface">
                  <Sparkles size={12} className="text-text-primary" />
                  Diagnóstico de Equipamentos · IA
                </div>

                <h1 className="mb-4 text-5xl sm:text-6xl font-semibold tracking-tight text-text-primary">
                  <Typewriter
                    text={[
                      "Não gela?",
                      "Fazendo barulho?",
                      "Compressor parado?",
                      "Porta com problema?",
                      "Vazando gás?",
                    ]}
                    speed={60}
                    deleteSpeed={35}
                    waitTime={2000}
                    cursorChar="_"
                    cursorClassName="ml-0.5 text-text-primary"
                  />
                </h1>
                <p className="text-sm text-muted mb-8 leading-relaxed">
                  Informe o defeito relatado pelo cliente e o tipo de
                  equipamento. A IA sugere os defeitos constatados mais
                  prováveis com base no histórico de ordens de serviço.
                </p>

                <FilterForm onAnalyze={handleAnalyze} isLoading={isLoading} />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="flex-shrink-0 flex items-center justify-center gap-2.5 py-2.5 border-t border-border bg-main/80 backdrop-blur-sm">
          <img src="/logo.svg" alt="Telecontrol AI" className="logo-telecontrol w-5 h-5 opacity-70" />
          <span className="text-xs text-muted">
            Telecontrol AI &copy; {new Date().getFullYear()} &middot; Diagnóstico de Equipamentos
          </span>
        </footer>
      </main>
    </div>
  );
}

