import { NextRequest, NextResponse } from "next/server";

interface WebSearchRequest {
  texto_cliente: string;
  tipo_produto?: string | null;
  segmento?: string | null;
  regiao?: string | null;
  top_defeitos?: string[];
  exemplos_dataset?: string[];
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

    // Mock response - simulando busca web contextual
    const data = {
      status: "ok",
      resultados: [
        {
          title: "Diagnóstico baseado em histórico interno",
          url: "https://suaempresa.com/kb/diagnostico",
          content: "Análise contextualizada usando dados históricos de ordens de serviço similares. Recomendações técnicas baseadas em padrões de falhas identificadas.",
        },
        {
          title: "Manual técnico - Solução de problemas",
          url: "https://suaempresa.com/manuais/troubleshooting",
          content: "Guia passo-a-passo para diagnóstico rápido. Inclui checklist de verificação e procedimentos recomendados.",
        },
      ],
    };

    return NextResponse.json(data);
  } catch (error) {
    console.error("[web-search] Erro interno:", error);
    return NextResponse.json(
      {
        error: "Erro ao processar busca web",
      },
      { status: 500 }
    );
  }
}
