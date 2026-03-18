import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

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
}

export async function POST(req: NextRequest) {
  try {
    const body: PredictRequest = await req.json();

    if (!body.texto_cliente || body.texto_cliente.trim() === "") {
      return NextResponse.json(
        { error: "texto_cliente é obrigatório" },
        { status: 400 }
      );
    }

    // ── Faz proxy para o backend FastAPI ──
    // Envia todos os filtros disponíveis, o backend decide se usa ou não
    const response = await fetch(`${BACKEND_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        texto_cliente: body.texto_cliente,
        // Filtros opcionais (ajudam o modelo a refinar a classificação)
        tipo_produto: body.tipo_produto || undefined,
        segmento: body.segmento || undefined,
        regiao: body.regiao || undefined,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      console.error("[predict] Erro do backend:", error);
      return NextResponse.json(
        {
          error: error.detail || "Erro ao processar requisição no backend",
        },
        { status: response.status }
      );
    }

    const data: PredictResponse = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error("[predict] Erro interno:", error);
    return NextResponse.json(
      {
        error: "Erro ao conectar ao backend. Verifique se o servidor está rodando em localhost:8000",
      },
      { status: 500 }
    );
  }
}
