"use client";

import { useState } from "react";
import clsx from "clsx";
import { Zap, Loader2 } from "lucide-react";

export interface FilterValues {
  defeitoReclamado: string;
  tipoProduto: string;
  segmento: string;
  regiao: string;
}

interface FilterFormProps {
  onAnalyze: (filters: FilterValues) => void;
  isLoading: boolean;
  compact?: boolean;
}

const PRODUTOS = [
  "Expositor Refrigerado",
  "Freezer Vertical",
  "Cooler de Bebidas",
  "Mini Refrigerador",
  "Bebedouro Industrial",
  "Câmara Fria",
];

const SEGMENTOS = [
  "PDV (Bar / Restaurante)",
  "Supermercado",
  "Distribuidora",
  "CD (Centro de Distribuição)",
  "Evento",
];

const REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"];

const SUGESTOES_DEFEITO = [
  "Não gela",
  "Com ruído alto",
  "Congelando",
  "Equipamento contaminado",
  "Lâmpada não acende",
  "Dando choque",
  "Porta com problema",
  "Cheirando queimado",
];

export default function FilterForm({
  onAnalyze,
  isLoading,
  compact,
}: FilterFormProps) {
  const [filters, setFilters] = useState<FilterValues>({
    defeitoReclamado: "",
    tipoProduto: "",
    segmento: "",
    regiao: "",
  });

  const set = (key: keyof FilterValues, value: string) =>
    setFilters((prev) => ({ ...prev, [key]: value }));

  const canSubmit =
    filters.defeitoReclamado.trim() && !isLoading;

  return (
    <div className={clsx("w-full", compact ? "space-y-3" : "space-y-5")}>
      {!compact && (
        <div>
          <h2 className="text-base font-semibold text-text-primary">
            Diagnosticar equipamento
          </h2>
          <p className="text-sm text-muted mt-0.5">
            Informe o defeito relatado e o tipo de equipamento. A IA sugere
            os defeitos constatados mais prováveis com base no histórico de OS.
          </p>
        </div>
      )}

      {/* Defeito reclamado */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-text-secondary">
          Defeito reclamado pelo cliente{" "}
          <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          placeholder="Ex: não gela, com ruído alto, cheirando queimado..."
          value={filters.defeitoReclamado}
          onChange={(e) => set("defeitoReclamado", e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && canSubmit) onAnalyze(filters);
          }}
          className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary placeholder:text-muted outline-none focus:border-text-primary/25 focus:shadow-[0_0_0_2px_rgba(17,17,17,0.06)] transition-all"
        />
        {!compact && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {SUGESTOES_DEFEITO.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => set("defeitoReclamado", s)}
                className="text-xs px-2.5 py-1 rounded-full border border-border text-muted hover:border-text-secondary/40 hover:text-text-secondary transition-all"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Tipo de produto + Segmento */}
      <div
        className={clsx(
          "grid gap-3",
          compact ? "grid-cols-1" : "grid-cols-2"
        )}
      >
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-text-secondary">
            Tipo de equipamento
          </label>
          <select
            value={filters.tipoProduto}
            onChange={(e) => set("tipoProduto", e.target.value)}
            className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary outline-none focus:border-text-primary/25 transition-all appearance-none"
          >
            <option value="">Selecionar...</option>
            {PRODUTOS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-text-secondary">
            Segmento
          </label>
          <select
            value={filters.segmento}
            onChange={(e) => set("segmento", e.target.value)}
            className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary outline-none focus:border-text-primary/25 transition-all appearance-none"
          >
            <option value="">Selecionar...</option>
            {SEGMENTOS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Região */}
      {!compact && (
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-text-secondary">
            Região (opcional)
          </label>
          <select
            value={filters.regiao}
            onChange={(e) => set("regiao", e.target.value)}
            className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary outline-none focus:border-text-primary/25 transition-all appearance-none"
          >
            <option value="">Qualquer região</option>
            {REGIOES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Submit */}
      <button
        type="button"
        onClick={() => canSubmit && onAnalyze(filters)}
        disabled={!canSubmit}
        className={clsx(
          "w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all",
          canSubmit
            ? "bg-text-primary text-white hover:bg-accent-hover cursor-pointer"
            : "bg-surface border border-border text-muted cursor-not-allowed opacity-50"
        )}
      >
        {isLoading ? (
          <>
            <Loader2 size={15} className="animate-spin" />
            Analisando...
          </>
        ) : (
          <>
            <Zap size={15} />
            Analisar com IA
          </>
        )}
      </button>
    </div>
  );
}
