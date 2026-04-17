import { NextRequest, NextResponse } from "next/server";

function getBackendUrl() {
  const configured = process.env.BACKEND_URL?.trim();
  if (configured) return configured;

  // Em dev local, mantém conveniência com FastAPI rodando na porta 8000.
  if (process.env.NODE_ENV !== "production") return "http://localhost:8000";

  return null;
}

interface WebSearchRequest {
  texto_cliente: string;
  tipo_produto?: string | null;
  segmento?: string | null;
  regiao?: string | null;
  top_defeitos?: string[];
  exemplos_dataset?: string[];
}

const USE_ML_MOCK = process.env.USE_ML_MOCK?.toLowerCase() === "true" || process.env.USE_ML_MOCK === "1";

function getMockWebSearch() {
  return {
    resultados: [
      {
        url: "https://suaempresa.com/manuais/compressor.pdf",
        title: "Manual Técnico - Compressor e Diagnóstico",
        content: "Guia completo para diagnóstico e manutenção de compressores em refrigeração comercial.",
      },
      {
        url: "https://suaempresa.com/diagnostico/evaporador",
        title: "Checklist de Inspeção - Evaporador",
        content: "Procedimento passo a passo para inspecionar e identificar vazamentos no evaporador.",
      },
      {
        url: "https://suaempresa.com/termostato-calibracao",
        title: "Calibração de Termostato",
        content: "Como calibrar corretamente o termostato para manter temperatura estável.",
      },
    ],
    status: "mock",
    query_usada: "Mock search - modo simulação ativo",
    query_secundaria: "Mock search alternativo",
  };
}

export async function POST(req: NextRequest) {
  try {
    const body: WebSearchRequest = await req.json();

    if (!body.texto_cliente || body.texto_cliente.trim() === "") {
      return NextResponse.json(
        { error: "texto_cliente é obrigatório" },
        { status: 400 }
      );
    }

    // Mock mode: return simulated web search results without calling any backend
    if (USE_ML_MOCK) {
      console.log("[web-search] Mock mode ativo, retornando dados simulados");
      return NextResponse.json(getMockWebSearch());
    }

    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      return NextResponse.json(
        {
          error: "BACKEND_URL não configurado no ambiente de produção.",
        },
        { status: 503 }
      );
    }

    const topDefeitos = Array.isArray(body.top_defeitos) ? body.top_defeitos : [];
    const exemplosDataset = Array.isArray(body.exemplos_dataset) ? body.exemplos_dataset : [];

    if (topDefeitos.length === 0 && exemplosDataset.length === 0) {
      return NextResponse.json(
        {
          error: "Contexto obrigatório ausente. Faça a análise com IA primeiro para enviar contexto dos datasets.",
          status: "missing_context",
          resultados: [],
        },
        { status: 400 }
      );
    }

    const response = await fetch(`${backendUrl}/web-search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        texto_cliente: body.texto_cliente,
        tipo_produto: body.tipo_produto ?? null,
        segmento: body.segmento ?? null,
        regiao: body.regiao ?? null,
        top_defeitos: topDefeitos,
        exemplos_dataset: exemplosDataset,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        {
          error: error.detail || "Erro ao processar busca web no backend",
        },
        { status: response.status }
      );
    }

    const data = await response.json();

    if (data?.status && data.status !== "ok" && data.status !== "fallback_context" && data.status !== "low_context") {
      const statusMessage =
        data.status === "missing_tavily_key"
          ? "Chave TAVILY_API_KEY ausente no backend"
          : data.status === "no_question"
          ? "Consulta vazia para busca web"
          : data.status === "no_results"
          ? "Nenhum resultado encontrado na busca web"
          : "Falha ao executar busca web no backend";

      return NextResponse.json(
        {
          error: statusMessage,
          status: data.status,
          resultados: Array.isArray(data.resultados) ? data.resultados : [],
        },
        { status: data.status === "no_results" ? 200 : 502 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("[web-search] Erro interno:", error);
    return NextResponse.json(
      {
        error: "Erro ao conectar ao backend para busca web",
      },
      { status: 500 }
    );
  }
}
