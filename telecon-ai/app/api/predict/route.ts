import { NextRequest, NextResponse } from "next/server";

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
    const body: PredictRequest = await req.json();

    const hasText = body.texto_cliente && body.texto_cliente.trim() !== "";
    const hasFilter = body.tipo_produto || body.segmento || body.regiao;

    if (!hasText && !hasFilter) {
      return NextResponse.json(
        { error: "Por favor, forneça a reclamação do cliente ou selecione pelo menos um filtro." },
        { status: 400 }
      );
    }

    // Mock response - simulando classificador
    const data: PredictResponse = {
      resultados: [
        {
          rank: 1,
          defeito_sugerido: "Compressor com defeito",
          confianca: 0.85,
          confianca_pct: 85,
          documentacao: "https://suaempresa.com/manuais/compressor.pdf",
          descricao_llm: "Análise baseada em histórico de ordens de serviço similares.",
          acao_recomendada_llm: "Inspecionar funcionamento do compressor. Consultar manual técnico.",
        },
        {
          rank: 2,
          defeito_sugerido: "Termostato com defeito",
          confianca: 0.72,
          confianca_pct: 72,
          documentacao: "https://suaempresa.com/manuais/termostato.pdf",
          descricao_llm: "Possível falha no sensor de temperatura.",
          acao_recomendada_llm: "Verificar calibração do termostato.",
        },
        {
          rank: 3,
          defeito_sugerido: "Evaporador obstruído",
          confianca: 0.65,
          confianca_pct: 65,
          documentacao: "https://suaempresa.com/manuais/evaporador.pdf",
          descricao_llm: "Possível bloqueio no fluxo de ar.",
          acao_recomendada_llm: "Realizar limpeza preventiva do evaporador.",
        },
      ],
      texto_analisado: body.texto_cliente || "",
      total_classes: 15,
      total_registros: 164,
      modelo_ativo: "randomforest",
      sugere_busca: false,
    };

    return NextResponse.json(data);
  } catch (error) {
    console.error("[predict] Erro interno:", error);
    return NextResponse.json(
      {
        error: "Erro ao processar requisição.",
      },
      { status: 500 }
    );
  }
}
