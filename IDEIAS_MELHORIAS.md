# Ideias de Melhoria — TeleControl AI

## 1. Dados & Modelo

### 1.1 Mais dados de treinamento
- O dataset atual possui **~119 amostras úteis** (≥ 3 por classe) — muito pouco para 26 classes.
- **Ação**: coletar mais OS (ordens de serviço) reais; objetivo mínimo de **50-100 amostras/classe**.
- Considerar técnicas de **data augmentation** em texto (ex.: parafrasear com LLM, sinônimos técnicos).

### 1.2 Modelo multilíngue / PT-BR nativo
- `all-MiniLM-L6-v2` foi treinado predominantemente em inglês.
- Substituir por **`paraphrase-multilingual-MiniLM-L12-v2`** (suporta PT-BR nativamente) ou **`rufimelo/bert-large-portuguese-cased-sts`**.
- Alternativa mais leve: **`neuralmind/bert-base-portuguese-cased`** via sentence-transformers.

### 1.3 Fine-tuning do classificador
- Com mais dados, experimentar **SVM com kernel RBF** ou **XGBoost** em cima dos embeddings.
- Avaliar com **cross-validation estratificada** (k=5) e métricas por classe (F1-weighted).

### 1.4 Retreinamento automático
- Toda vez que o usuário confirmar um diagnóstico via `/feedback`, acumular os dados.
- Implementar um **job periódico** (ex.: cron semanal) que retreina e re-avalia o modelo.
- Comparar acurácia antes/depois antes de promover o modelo novo para produção.

---

## 2. Backend & API

### 2.1 Banco de dados para feedback e logs
- Trocar o armazenamento em memória por **PostgreSQL** (via Supabase já configurado no `.env`) ou **SQLite** para ambiente local.
- Persistir: reclamação, defeito previsto, defeito correto, timestamp, confiança.

### 2.2 Cache de requisições LLM
- Guardar respostas Groq em cache (ex.: **Redis** ou `functools.lru_cache` com timeout).
- Evitar cobranças duplicadas para reclamações iguais ou muito similares (cosseno > 0.95).

### 2.3 Async no endpoint `/predict`
- Tornar o handler `async` e usar `await asyncio.to_thread(...)` para as operações de ML (CPU-bound) não bloquearem o event loop.
- A chamada ao Groq já é rápida, mas pode ser `asyncio.wait_for` com timeout de 5 s.

### 2.4 Versionamento de modelo
- Salvar modelos com metadados: data de treino, acurácia, número de amostras.
- Endpoint `/modelo/info` retornando essas informações para o frontend.

### 2.5 Rate limiting & auth básica
- Adicionar **`slowapi`** para rate limiting no endpoint `/predict`.
- Implementar autenticação simples (API Key no header) antes de expor em produção.

---

## 3. LLM & Geração de Texto

### 3.1 Enriquecer todos os 3 resultados
- Atualmente somente o rank-1 é enriquecido pelo LLM.
- Possível melhoria: gerar breves descrições para rank-2 e rank-3 também (com um único prompt batch).

### 3.2 Fallback automático de LLM
- Se Groq retornar erro ou timeout, tentar **Ollama local** (`llama3:8b`) como segundo fallback.
- Cadeia: Groq → Ollama → texto estático gerado por templates.

### 3.3 Extração estruturada de diagnóstico
- Pedir ao LLM que retorne campos adicionais como:
  - `peças_necessarias` (lista de componentes prováveis)
  - `urgencia` (baixa / média / alta)
  - `tempo_estimado_reparo` (em horas)
- Apresentar essas informações em cards separados no frontend.

### 3.4 Histórico de conversa
- Transformar a interface em um **chat multi-turno**: o técnico pode refinar o diagnóstico com novas informações ("o compressor liga mas não resfria").
- Manter contexto no estado do frontend e enviar histórico ao backend.

---

## 4. Frontend & UX

### 4.1 Indicador de confiança visual
- Substituir o percentual simples por uma **barra de progresso colorida**: verde (> 60%), amarelo (30-60%), vermelho (< 30%).

### 4.2 Botão "Este diagnóstico foi correto?"
- Logo abaixo do resultado principal, dois botões: ✅ Correto / ❌ Errado.
- Se errado, abrir dropdown para o técnico selecionar o defeito real → chama `/feedback`.

### 4.3 Histórico de consultas locais
- Guardar as últimas consultas em `localStorage`.
- Exibir no `Sidebar` como histórico de sessão.

### 4.4 Modo offline / PWA
- Configurar `next-pwa` para cache de assets.
- Exibir mensagem amigável quando o backend estiver offline.

### 4.5 Tema escuro / claro
- Já existe `theme-provider.tsx`. Finalizar a implementação e persistir preferência em `localStorage`.

### 4.6 Internacionalização (i18n)
- Adicionar suporte a EN-US para uso em clientes internacionais via `next-intl`.

---

## 5. DevOps & Infraestrutura

### 5.1 Docker Compose finalizado
- Orquestrar `api` (FastAPI) + `web` (Next.js) num único `docker-compose.yml` com healthchecks.
- Variáveis de ambiente via `.env` injetado no compose.

### 5.2 CI/CD básico
- Workflow GitHub Actions: lint → testes → build Docker → push para registry.
- Deploy automático para **Azure Container Instances** ou **Railway.app**.

### 5.3 Monitoramento de modelo (MLOps)
- Integrar **MLflow** para rastrear experimentos de treino (parâmetros, métricas, artefatos).
- Dashboard simples com acurácia ao longo do tempo.

### 5.4 Observabilidade do backend
- Adicionar **Prometheus + Grafana** (ou **OpenTelemetry**) para métricas de latência, erros e uso do endpoint `/predict`.

---

## 6. Segurança

| Item | Ação |
|------|------|
| GROQ_API_KEY exposta | Garantir que `.env` está no `.gitignore` |
| CORS aberto | Restringir `allow_origins` ao domínio de produção |
| Inputs sem sanitização | Limitar `texto_cliente` a 500 chars, strip HTML |
| Sem autenticação | Adicionar JWT ou API Key antes de deploy público |

---

## 7. Prioridade Sugerida

| Prioridade | Item |
|-----------|------|
| 🔴 Alta | Mais dados de treinamento (1.1) |
| 🔴 Alta | Banco de dados para feedback (2.1) |
| 🟡 Média | Modelo PT-BR nativo (1.2) |
| 🟡 Média | Botão de feedback no frontend (4.2) |
| 🟡 Média | Docker Compose finalizado (5.1) |
| 🟢 Baixa | Histórico local (4.3) |
| 🟢 Baixa | Rate limiting (2.5) |
| 🟢 Baixa | MLflow (5.3) |
