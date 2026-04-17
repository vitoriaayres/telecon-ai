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
}

export async function POST(req: NextRequest) {
  try {
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
