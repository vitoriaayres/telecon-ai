import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

# Load environment variables
load_dotenv()

# 1. Definimos a estrutura de dados que o LLM DEVE retornar
class ClassificacaoDefeito(BaseModel):
    codigo_defeito: str = Field(description="Um código curto para o defeito (ex: TELA_QUEBRADA, PLACA_CURTO).")
    nome_defeito: str = Field(description="O nome técnico e claro do defeito constatado.")
    causa_raiz: list[str] = Field(description="Termos exatos da reclamação do cliente que justificam essa decisão.")
    confianca: float = Field(description="Nível de confiança na resposta, de 0.0 a 1.0.")

def analisar_reclamacao(texto_cliente: str, caracteristicas_produto: str) -> ClassificacaoDefeito:
    """
    Recebe a reclamação do cliente e as características do produto
    e retorna a classificação estruturada do defeito.
    """
    
    # Configure Azure OpenAI
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
        temperature=0
    )
    
    # Forçamos o LLM a seguir a estrutura do Pydantic
    llm_estruturado = llm.with_structured_output(ClassificacaoDefeito)

    # Criamos o template de instrução
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um assistente técnico sênior. 
        Sua tarefa é ler o relato do cliente e as características do produto e sugerir o defeito mais provável.
        Seja preciso e extraia a causa raiz diretamente do texto do cliente."""),
        ("user", "Produto: {produto}\nRelato do Cliente: {relato}")
    ])

    # Montamos e executamos a Chain
    chain = prompt | llm_estruturado
    
    resultado = chain.invoke({
        "produto": caracteristicas_produto,
        "relato": texto_cliente
    })
    
    return resultado

# --- Teste Rápido ---
if __name__ == "__main__":
    # Simulação de um teste local
    reclamacao = "O celular caiu no chão ontem e agora a imagem tá toda listrada e o touch não funciona nas bordas."
    produto = "Smartphone Modelo X, Tela OLED"
    
    resposta = analisar_reclamacao(reclamacao, produto)
    
    print(f"Defeito: {resposta.nome_defeito} ({resposta.codigo_defeito})")
    print(f"Causa Raiz (Termos-chave): {resposta.causa_raiz}")
    print(f"Confiança: {resposta.confianca}")