#!/bin/bash
# quick_start.sh
# Quick Start Script para Telecontrol - Azure ML

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         QUICK START - TELECONTROL + AZURE ML                     ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções
print_step() {
    echo -e "${BLUE}▶️ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# 1. Verificar pré-requisitos
print_step "Verificando pré-requisitos..."

if ! command -v python &> /dev/null; then
    print_error "Python não instalado"
    exit 1
fi
print_success "Python encontrado: $(python --version)"

if ! command -v az &> /dev/null; then
    print_warning "Azure CLI não instalado"
    print_step "Instale em: https://aka.ms/azcli"
    read -p "Pressione ENTER quando instalado..."
fi

if ! command -v docker &> /dev/null; then
    print_warning "Docker não instalado (opcional)"
fi

# 2. Criar virtual environment
print_step "Criando virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    print_success "Virtual environment criado"
else
    print_success "Virtual environment já existe"
fi

# Ativar venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
print_success "Virtual environment ativado"

# 3. Instalar dependências
print_step "Instalando dependências..."
pip install -q -r requirements.txt
print_success "Dependências instaladas"

# 4. Executar testes locais
print_step "Executando testes locais..."
python test_tudo_antes_azure.py
if [ $? -ne 0 ]; then
    print_error "Testes falharam. Corrija os erros e tente novamente."
    exit 1
fi
print_success "Testes locais passaram"

# 5. Verificar .env.azure
print_step "Verificando .env.azure..."
if [ ! -f ".env.azure" ]; then
    print_error ".env.azure não encontrado"
    exit 1
fi

# Verificar se está preenchido
if grep -q "AZURE_SUBSCRIPTION_ID=<seu" .env.azure; then
    print_error ".env.azure não foi preenchido"
    echo "   Edite .env.azure e preencha os valores:"
    echo "   - AZURE_SUBSCRIPTION_ID"
    echo "   - AZURE_RESOURCE_GROUP"
    echo "   - AZURE_ML_WORKSPACE_NAME"
    echo "   - AZURE_STORAGE_ACCOUNT_NAME"
    exit 1
fi
print_success ".env.azure preenchido"

# 6. Testar conectividade Azure
print_step "Testando conectividade com Azure..."
python test_azure_integration.py
if [ $? -ne 0 ]; then
    print_error "Falha de conectividade Azure"
    print_warning "Execute: az login"
    exit 1
fi
print_success "Conectividade Azure OK"

# 7. Menu de opções
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                     PRÓXIMOS PASSOS                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Escolha uma opção:"
echo ""
echo "1) Setup Azure (criar infraestrutura)"
echo "   python setup_azure_ml.py"
echo ""
echo "2) Testar API Localmente"
echo "   python trainamento_modelo.py"
echo "   uvicorn api:app --reload"
echo ""
echo "3) Upload de Dados"
echo "   python upload_dados.py"
echo ""
echo "4) Treinar no Azure ML (30min)"
echo "   python training_pipeline.py"
echo ""
echo "5) Deploy em Azure Container Instances"
echo "   python deploy_aci.py"
echo ""
echo "6) Ver Documentação"
echo "   cat GUIA_AZURE_ML.md"
echo ""
echo "0) Sair"
echo ""
read -p "Digite sua opção (0-6): " opcao

case $opcao in
    1)
        print_step "Setup Azure..."
        python setup_azure_ml.py
        ;;
    2)
        print_step "Iniciando API local..."
        python trainamento_modelo.py
        uvicorn api:app --reload
        ;;
    3)
        print_step "Upload de dados..."
        python upload_dados.py
        ;;
    4)
        print_step "Treinando no Azure ML..."
        python training_pipeline.py
        ;;
    5)
        print_step "Deploying..."
        python deploy_aci.py
        ;;
    6)
        if command -v cat &> /dev/null; then
            cat GUIA_AZURE_ML.md | less
        else
            print_warning "Use um editor para ler GUIA_AZURE_ML.md"
        fi
        ;;
    0)
        print_success "Até logo!"
        exit 0
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

print_success "Concluído!"
