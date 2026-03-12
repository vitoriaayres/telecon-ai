"use client";

import clsx from "clsx";
import { ChevronDown, ChevronUp, Copy, Check, ExternalLink, Wrench, FileText } from "lucide-react";
import { useState } from "react";
import FeedbackWidget from "@/components/FeedbackWidget";

export interface ClassificationResult {
  rank: number;
  defect: string;
  confidenceRel: number;   // 0-100 relativo ao rank 1
  confidenceAbs: number;   // % absoluto retornado pela API
  description: string;
  recommendedAction: string;
  manualUrl: string;
}

export interface AnalysisOutput {
  filters: {
    defeitoReclamado: string;
    tipoProduto: string;
    segmento: string;
    regiao: string;
  };
  results: ClassificationResult[];
  totalAnalyzed: number;
  modelUsed: string;
}

interface ResultsPanelProps {
  output: AnalysisOutput;
}

export default function ResultsPanel({ output }: ResultsPanelProps) {
  const [top, ...alternativas] = output.results;

  return (
    <div className="space-y-5 animate-slide-up">
      {/* Cabeçalho */}
      <div className="flex items-start justify-between gap-4 pb-4 border-b border-border">
        <div>
          <p className="text-xs text-muted mb-0.5">Reclamação analisada</p>
          <p className="text-sm font-semibold text-text-primary">
            &ldquo;{output.filters.defeitoReclamado}&rdquo;
          </p>
          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            {output.filters.tipoProduto && <Tag>{output.filters.tipoProduto}</Tag>}
            {output.filters.segmento && <Tag>{output.filters.segmento}</Tag>}
            {output.filters.regiao && <Tag>{output.filters.regiao}</Tag>}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="text-xs text-muted mb-0.5">Modelo ativo</p>
          <p className="text-xs font-medium text-text-secondary">{output.modelUsed}</p>
        </div>
      </div>

      {/* Diagnóstico principal */}
      {top && <PrimaryCard result={top} />}

      {/* Hipóteses alternativas */}
      {alternativas.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted uppercase tracking-wider">
            Hipóteses alternativas
          </p>
          {alternativas.map((r) => (
            <AlternativeCard key={r.defect} result={r} />
          ))}
        </div>
      )}

      {/* Rodapé */}
      <p className="text-xs text-muted pt-1 leading-relaxed">
        Resultado gerado por IA com base em{" "}
        {output.totalAnalyzed.toLocaleString("pt-BR")} ordens de serviço.
        Valide com técnico especializado antes de qualquer ação em campo.
      </p>
    </div>
  );
}

/* ─── Card do diagnóstico principal ─────────────────────────────────────── */
function PrimaryCard({ result }: { result: ClassificationResult }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(
      `Defeito: ${result.defect}\n\n${result.description}\n\nAção recomendada: ${result.recommendedAction}`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const barColor =
    result.confidenceRel >= 70
      ? "bg-emerald-500"
      : result.confidenceRel >= 40
      ? "bg-amber-400"
      : "bg-zinc-400";

  return (
    <div className="bg-surface border border-text-primary/20 rounded-xl overflow-hidden">
      {/* Label topo */}
      <div className="px-4 pt-3 pb-1 flex items-center justify-between">
        <span className="text-xs font-semibold text-text-secondary uppercase tracking-widest">
          Diagnóstico Principal
        </span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary transition-colors"
        >
          {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
          {copied ? "Copiado" : "Copiar"}
        </button>
      </div>

      {/* Nome do defeito */}
      <div className="px-4 pb-3">
        <p className="text-lg font-bold text-text-primary leading-tight">{result.defect}</p>
        <div className="mt-2 mb-0.5 flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
            <div
              className={clsx("h-full rounded-full transition-all duration-700", barColor)}
              style={{ width: `${result.confidenceRel}%` }}
            />
          </div>
          <span className="text-xs text-muted tabular-nums">{result.confidenceAbs}%</span>
        </div>
      </div>

      {/* Descrição e ação */}
      <div className="border-t border-border px-4 py-3 space-y-3">
        <div>
          <div className="flex items-center gap-1.5 mb-1">
            <FileText size={12} className="text-muted" />
            <p className="text-xs font-medium text-text-secondary">O que pode estar acontecendo</p>
          </div>
          <p className="text-sm text-text-primary leading-relaxed">{result.description}</p>
        </div>

        <div className="bg-main rounded-xl px-3 py-2.5">
          <div className="flex items-center gap-1.5 mb-1">
            <Wrench size={12} className="text-muted" />
            <p className="text-xs font-medium text-text-secondary">Ação recomendada</p>
          </div>
          <p className="text-sm text-text-primary leading-relaxed">{result.recommendedAction}</p>
        </div>

        {result.manualUrl.startsWith("http") && (
          <a
            href={result.manualUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary transition-colors"
          >
            <ExternalLink size={12} />
            Manual técnico
          </a>
        )}

        {/* Feedback da resposta da IA */}
        <FeedbackWidget
          resultId={`primary-${result.defect}`}
          context={`Diagnóstico Principal: ${result.defect}`}
        />
      </div>
    </div>
  );
}

/* ─── Card de hipótese alternativa ──────────────────────────────────────── */
function AlternativeCard({ result }: { result: ClassificationResult }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-main/60 transition-colors"
      >
        <span className="flex-shrink-0 w-5 h-5 rounded-full bg-border flex items-center justify-center text-xs font-bold text-text-secondary">
          {result.rank}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-text-primary truncate">{result.defect}</p>
          <div className="mt-1 h-1 bg-border rounded-full overflow-hidden w-28">
            <div
              className="h-full bg-zinc-400 rounded-full"
              style={{ width: `${result.confidenceRel}%` }}
            />
          </div>
        </div>
        <span className="text-xs text-muted tabular-nums flex-shrink-0 mr-1">
          {result.confidenceAbs}%
        </span>
        {expanded ? (
          <ChevronUp size={14} className="text-muted flex-shrink-0" />
        ) : (
          <ChevronDown size={14} className="text-muted flex-shrink-0" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-3 border-t border-border space-y-2.5 pt-3 animate-fade-in">
          <div>
            <div className="flex items-center gap-1.5 mb-1">
              <FileText size={11} className="text-muted" />
              <p className="text-xs font-medium text-text-secondary">Possível causa</p>
            </div>
            <p className="text-sm text-text-primary leading-relaxed">{result.description}</p>
          </div>
          <div className="bg-main rounded-xl px-3 py-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Wrench size={11} className="text-muted" />
              <p className="text-xs font-medium text-text-secondary">Ação sugerida</p>
            </div>
            <p className="text-sm text-text-primary leading-relaxed">{result.recommendedAction}</p>
          </div>
          {result.manualUrl.startsWith("http") && (
            <a
              href={result.manualUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-text-secondary transition-colors"
            >
              <ExternalLink size={12} />
              Manual técnico
            </a>
          )}

          {/* Feedback da hipótese alternativa */}
          <FeedbackWidget
            resultId={`alt-${result.rank}-${result.defect}`}
            context={`Hipótese #${result.rank}: ${result.defect}`}
          />
        </div>
      )}
    </div>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs px-2 py-0.5 rounded-full bg-main border border-border text-text-secondary">
      {children}
    </span>
  );
}

