# TELECON AI

Interface de chat com IA moderna e limpa, inspirada no ChatGPT, desenvolvida com **Next.js 14**, **Tailwind CSS** e pronta para deploy no **Vercel**.

---

## Funcionalidades

- Interface de chat com tema escuro moderno
- Sidebar recolhível com histórico de conversas por data
- Resposta com efeito de streaming (digitação em tempo real)
- Suporte a Markdown nas respostas (tabelas, código, listas, etc.)
- Ações nas mensagens: copiar, curtir, regenerar
- Seletor de modelos de IA
- Tela de boas-vindas com sugestões de prompts
- Totalmente responsivo

---

## Rodando localmente

```bash
npm install
npm run dev
```

Acesse: [http://localhost:3000](http://localhost:3000)

---

## Deploy no Vercel

### Opção 1 — Vercel CLI

```bash
npm install -g vercel
vercel
```

### Opção 2 — GitHub + Vercel Dashboard

1. Suba este repositório para o GitHub
2. Acesse [vercel.com](https://vercel.com) e importe o repositório
3. O Vercel detecta automaticamente o Next.js e faz o deploy

---

## Conectando sua API de IA

Edite a função `fetchAIResponse` em [app/page.tsx](app/page.tsx) para integrar com sua API real:

```typescript
// Exemplo com OpenAI-compatible API
const response = await fetch("/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message }),
  signal,
});
```

Crie o arquivo `app/api/chat/route.ts` para implementar a rota da sua API.

---

## Estrutura do projeto

```
├── app/
│   ├── layout.tsx       # Layout raiz com metadados
│   ├── page.tsx         # Página principal (lógica do chat)
│   └── globals.css      # Estilos globais + Tailwind
├── components/
│   ├── Sidebar.tsx      # Sidebar com histórico
│   ├── ChatArea.tsx     # Área de mensagens + tela de boas-vindas
│   ├── MessageBubble.tsx # Bolha de mensagem com Markdown
│   └── InputArea.tsx    # Caixa de input com ações
├── vercel.json          # Configuração do Vercel
└── tailwind.config.js   # Tema customizado
```

---

## Tecnologias

- [Next.js 14](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Markdown](https://github.com/remarkjs/react-markdown)
- [Lucide React](https://lucide.dev/)
- [Vercel](https://vercel.com/)
