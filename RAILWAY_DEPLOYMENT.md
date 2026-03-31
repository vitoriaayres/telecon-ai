# 🚀 TeleControl → Railway.app Deployment Guide

## Por que Railway?
✅ Suporta Docker (Backend FastAPI + Frontend Next.js)  
✅ Arquivos GRANDES OK (ML models de 150MB cabem tranquilamente)  
✅ Roteamento automático de porta (seu problema resolvido!)  
✅ Muito mais simples que Azure  
✅ Grátis para testar  

---

## PASSO 1: Preparar Repositório Git

### 1.1 - Verificar se está no Git
```bash
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
git status
```

Se NÃO estiver em repositório Git, crie um:
```bash
git init
git add .
git commit -m "Initial commit - TeleControl ready for Railway"
```

### 1.2 - Enviar para GitHub
1. Abra https://github.com/new
2. Crie repositório chamado `telecontrol` (público)
3. Copie os comandos que aparecem e rode no terminal:
```bash
git remote add origin https://github.com/SEU_USERNAME/telecontrol.git
git branch -M main
git push -u origin main
```

✅ Seu código agora está no GitHub!

---

## PASSO 2: Criar Conta Railway

1. Abra https://railway.app
2. Clique "Sign Up"
3. Use GitHub para login (mais fácil!)
4. Autorize Railway a acessar seus repositórios

✅ Conta criada!

---

## PASSO 3: Criar Projeto no Railway

### 3.1 - Dashboard
Após login, você está no Dashboard do Railway.

### 3.2 - Novo Projeto
Clique botão **"+ New Project"** → **"Deploy from GitHub"**

### 3.3 - Selecionar Repositório
- Escolha `telecontrol`
- Autorize se pedir

### 3.4 - Railway detecta Docker
Railway vai detectar o `docker-compose.yml` e `Dockerfile` automaticamente!

Se não detectar, você pode configurar manualmente (vamos abordar depois).

✅ Projeto criado!

---

## PASSO 4: Configurar Variáveis de Ambiente

Railway precisa das chaves do Azure OpenAI. No Dashboard:

1. Vá para **"Variables"**
2. Adicione estas variáveis:

```
AZURE_OPENAI_KEY=sua_chave_aqui
AZURE_OPENAI_ENDPOINT=https://breakfixtesteunimar.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini-2
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

3. Clique **"Save"**

✅ Variáveis configuradas!

**Dica**: Você já tem essas chaves em `.env` local. Procure por `AZURE_OPENAI_*` no seu projeto.

---

## PASSO 5: Deploy Automático

### 5.1 - Iniciar Deploy
No Dashboard, clique **"Deploy"**

Railway vai:
1. ✅ Clonar seu repositório do GitHub
2. ✅ Ler `docker-compose.yml`
3. ✅ Fazer build das imagens (backend + frontend)
4. ✅ Rodar os containers
5. ✅ Gerar URLs públicas

⏱️ **Tempo estimado**: 5-10 minutos na primeira vez (ML models são grandes)

### 5.2 - Monitorar Deploy
No Dashboard, você vai ver:
- `Building...` (fazendo build das imagens)
- `Deploying...` (rodando containers)
- `Running` (pronto! ✅)

Se der erro, clique em **"Logs"** para ver o que aconteceu.

---

## PASSO 6: Testar URLs Públicas

Após deploy completar, Railway te dá URLs:

**Frontend**: `https://seu-projeto-frontend.up.railway.app`
**Backend**: `https://seu-projeto-backend.up.railway.app`

### 6.1 - Testar Frontend
Abra a URL do frontend no navegador. Você deve ver a interface TeleControl!

### 6.2 - Testar Backend Health
Abra no navegador:
```
https://seu-projeto-backend.up.railway.app/health
```

Deve retornar:
```json
{"status": "ok"}
```

### 6.3 - Testar Previsão
Você pode usar o Frontend para fazer uma previsão, ou chamar via código:

**Python**:
```python
import requests

response = requests.post(
    "https://seu-projeto-backend.up.railway.app/predict",
    json={"defeito": "Fio desencapado"}
)
print(response.json())
```

**JavaScript/cURL**:
```bash
curl -X POST https://seu-projeto-backend.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"defeito": "Fio desencapado"}'
```

✅ Tudo funcionando!

---

## Passo 7: Conectar Frontend ↔ Backend

Se o Frontend está chamando o Backend, você precisa atualizar a URL.

### 7.1 - Buscar arquivo de configuração do Frontend
Procure no projeto por arquivos que configuram a URL da API:
```
telecon-ai/.env
telecon-ai/.env.local
telecon-ai/src/config.js
telecon-ai/src/lib/api.js
```

### 7.2 - Atualizar URL da API
Mude de:
```
http://localhost:8000
```

Para:
```
https://seu-projeto-backend.up.railway.app
```

### 7.3 - Fazer Commit e Push
```bash
git add .
git commit -m "Update backend URL for Railway deployment"
git push
```

Railway vai automaticamente fazer deploy novamente! ✅

---

## TROUBLESHOOTING

### ❌ "Deploy failing - Build error"
1. Clique em **"Logs"** para ver o erro exato
2. Procure por erros de `pip install` ou `npm install`
3. Verifique `requirements.txt` e `package.json`

### ❌ "Backend retorna 500 error"
1. Verifique se variáveis de ambiente estão corretas (AZURE_OPENAI_*)
2. Clique em **"Logs"** no Railway para ver o erro
3. Procure por erro de conexão com Azure OpenAI

### ❌ "Frontend não conecta com Backend"
1. Verifique a URL da API (deve ser https://, não http://)
2. Verifique CORS no backend (`api.py` linha 23-30)
3. Abra Console do navegador (F12) para ver erro exato

### ❌ "ML models não estão carregando"
1. Verifique se os arquivos `.pkl` estão no repositório Git
2. Rode `git lfs` se os arquivos forem muito grandes:
   ```bash
   git lfs install
   git lfs track "*.pkl"
   git add .gitattributes
   git commit -m "Add LFS tracking for ML models"
   git push
   ```

---

## Próximos Passos

1. **Domínio Customizado** (opcional)
   - Se quiser `telecontrol.com` em vez de `railway.app`
   - Railway permite conectar domínios pelo Dashboard

2. **Monitoramento**
   - Railway tem logs automáticos
   - Você pode ver CPU, memória, rede em tempo real

3. **Escalar**
   - Se tiver muitos usuários, aumentar o plano no Railway
   - Começa grátis (com limite de uso), paga conforme usa

---

## Resumo Rápido

| O que | Onde |
|------|-----|
| Criar repositório Git | GitHub.com |
| Criar conta | Railway.app |
| Deploy | Dashboard Railway → "Deploy" |
| Variáveis de Ambiente | Dashboard Railway → Variables |
| Testar | Abra as URLs públicas |
| Atualizar código | Git push → Railway faz deploy automático |

---

**Pronto!** 🎉 Seu TeleControl está na nuvem!

Se der erro em alguma etapa, me avisa qual foi o erro e o que vê nos Logs do Railway.
