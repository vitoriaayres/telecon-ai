import { NextRequest, NextResponse } from "next/server";

interface FeedbackPayload {
  resultId: string;
  value: "positive" | "negative" | null;
  comment: string;
  timestamp: number;
  context?: string;
}

// Em produção, persista em banco ou envie para serviço externo.
// Por enquanto, loga no servidor e retorna 200 — o client já salva no localStorage.
export async function POST(req: NextRequest) {
  try {
    const body: FeedbackPayload = await req.json();

    if (!body.resultId || !body.value) {
      return NextResponse.json({ error: "Payload inválido" }, { status: 400 });
    }

    // Log estruturado — visível nos logs do servidor (Vercel, PM2, etc.)
    console.log("[feedback]", {
      resultId: body.resultId,
      value: body.value,
      comment: body.comment ?? "",
      context: body.context ?? "",
      ts: new Date(body.timestamp).toISOString(),
    });

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "Erro interno" }, { status: 500 });
  }
}
