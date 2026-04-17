import { NextRequest, NextResponse } from "next/server";

function getBackendUrl() {
  const configured = process.env.BACKEND_URL?.trim();
  if (configured) return configured;

  // Em dev local, mantém conveniência com FastAPI rodando na porta 8000.
  if (process.env.NODE_ENV !== "production") return "http://localhost:8000";

  return null;
}

interface PredictRequest {
  texto_cliente: string;
  tipo_produto?: string | null;
  segmento?: string | null;
  regiao?: string | null;
}

interface PredictResponse {
  resultados: Array<{
    rank: number;
    defeito_sugerido: string;
    confianca: number;
    confianca_pct: number;
    documentacao: string;
    descricao_llm: string;
    acao_recomendada_llm: string;
  }>;
  texto_analisado: string;
  total_classes: number;
  total_registros: number;
  modelo_ativo: string;
  sugere_busca?: boolean;
  contexto_web?: {
    top_defeitos: string[];
    exemplos_dataset: string[];
  };
}

const USE_ML_MOCK = process.env.USE_ML_MOCK?.toLowerCase() === "true" || process.env.USE_ML_MOCK === "1";

const MOCK_DEFEITOS = [
  { defeito: "Compressor com defeito", confianca: 0.50 },
  { defeito: "Evaporador com vazamento", confianca: 0.35 },
  { defeito: "Termostato com defeito", confianca: 0.15 },
];

function getMockPrediction(textoCliente: string): PredictResponse {
  return {
    resultados: MOCK_DEFEITOS.map((c, i) => ({
      rank: i + 1,
      defeito_sugerido: c.defeito,
      confianca: c.confianca,
      confianca_pct: Math.round(c.confianca * 1000) / 10,
      documentacao: "",
      descricao_llm: "Possível causa identificada com base em sintomas similares em registros históricos.",
      acao_recomendada_llm: `Inspecionar o componente '${c.defeito}' e validar em bancada técnica.`,
    })),
    texto_analisado: textoCliente,
    total_classes: 3,
    total_registros: 1000,
    modelo_ativo: "mock-simulation",
    sugere_busca: true,
    contexto_web: {
      top_defeitos: MOCK_DEFEITOS.map((c) => c.defeito),
      exemplos_dataset: [
        "Equipamento não liga após queda de energia",
        "Temperatura oscilando sem controle",
        "Compressor rodando constantemente",
      ],
    },
  };
}

export async function POST(req: NextRequest) {
  try {
    const body: PredictRequest = await req.json();
    console.log("[predict] Requisição recebida:", body);

    const hasText = body.texto_cliente && body.texto_cliente.trim() !== "";
    const hasFilter = body.tipo_produto || body.segmento || body.regiao;

    if (!hasText && !hasFilter) {
      return NextResponse.json(
        { error: "Por favor, forneça a reclamação do cliente ou selecione pelo menos um filtro." },
        { status: 400 }
      );
    }

    // Mock mode: return simulated data without calling any backend
    if (USE_ML_MOCK) {
      console.log("[predict] Mock mode ativo, retornando dados simulados");
      const textoFinal = body.texto_cliente?.trim() || "";
      return NextResponse.json(getMockPrediction(textoFinal));
    }

    const backendUrl = getBackendUrl();
    console.log("[predict] NODE_ENV:", process.env.NODE_ENV, "| backendUrl:", backendUrl);
    
    if (!backendUrl) {
      console.error("[predict] BACKEND_URL não configurado");
      return NextResponse.json(
        {
          error: "BACKEND_URL não configurado no ambiente de produção.",
        },
        { status: 503 }
      );
    }

    console.log("[predict] Chamando backend em:", `${backendUrl}/predict`);
    
    const response = await fetch(`${backendUrl}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        texto_cliente: body.texto_cliente || "",
        tipo_produto: body.tipo_produto || undefined,
        segmento: body.segmento || undefined,
        regiao: body.regiao || undefined,
      }),
    });

    console.log("[predict] Resposta do backend - Status:", response.status, "OK:", response.ok);

    if (!response.ok) {
      const text = await response.text();
      console.error("[predict] Erro do backend (text):", text);
      let error: { detail?: string } = {};
      try {
        error = JSON.parse(text);
      } catch (e) {
        error = { detail: text || "Erro desconhecido do backend" };
      }
      return NextResponse.json(
        {
          error: error.detail || "Erro ao processar requisição no backend",
        },
        { status: response.status }
      );
    }

    const data: PredictResponse = await response.json();
    console.log("[predict] Resposta sucesso:", data?.resultados?.length, "resultados");

    return NextResponse.json(data);
  } catch (error) {
    console.error("[predict] Erro interno:", error);
    return NextResponse.json(
      {
        error: "Erro ao conectar ao backend de classificação.",
      },
      { status: 500 }
    );
  }
}
