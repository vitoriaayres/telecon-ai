"""
RAG System for Defect Classification
Retrieves similar historical cases from datasets and uses them as context for Azure OpenAI
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from pydantic import BaseModel, Field

load_dotenv()


class DefectClassificationResult(BaseModel):
    """Structured output from LLM"""
    defect_code: str = Field(description="Short code for the defect (e.g., TELA_QUEBRADA)")
    defect_name: str = Field(description="Clear technical name of the defect")
    root_cause: List[str] = Field(description="Key terms from customer complaint that justify this decision")
    confidence: float = Field(description="Confidence level from 0.0 to 1.0")
    reasoning: str = Field(description="Brief explanation of why this defect was chosen based on similar cases")


class RAGDefectClassifier:
    """
    RAG-based defect classifier that uses historical data as context for Azure OpenAI
    """
    
    def __init__(self):
        """Initialize RAG system with datasets and embeddings"""
        
        # Load datasets
        print("📚 Loading datasets...")
        self.df1 = self._load_dataset("DATASET/dataset_1.csv")
        self.df2 = self._load_dataset("DATASET/dataset_2.csv")
        
        # Combine datasets
        self.historical_cases = self._prepare_historical_data()
        print(f"✅ Loaded {len(self.historical_cases)} historical cases")
        
        # Initialize embeddings model (Portuguese-optimized)
        print("🔤 Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create vector store
        print("🗂️ Building vector database...")
        self.vectorstore = self._build_vectorstore()
        print("✅ RAG system initialized!")
        
        # Initialize Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            temperature=0
        )
        
        # Structured output
        self.structured_llm = self.llm.with_structured_output(DefectClassificationResult)
    
    def _load_dataset(self, filepath: str) -> Optional[pd.DataFrame]:
        """Load dataset with error handling"""
        try:
            if not os.path.exists(filepath):
                print(f"⚠️ Dataset not found: {filepath}")
                return None
            
            df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
            return df
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")
            return None
    
    def _prepare_historical_data(self) -> List[Dict]:
        """Prepare historical cases from datasets"""
        cases = []
        
        # Dataset 1: descricao_defeito_reclamado -> descricao_defeito_constatado_ref
        if self.df1 is not None:
            for _, row in self.df1.iterrows():
                try:
                    # Adjust these column names based on your actual CSV structure
                    complaint = str(row.get('descricao_defeito_reclamado', '') or 
                                  row.get('reclamacao', '') or 
                                  row.get('complaint', ''))
                    
                    actual_defect = str(row.get('descricao_defeito_constatado_ref', '') or 
                                      row.get('defeito_constatado', '') or 
                                      row.get('defect', ''))
                    
                    if complaint and actual_defect and complaint != 'nan' and actual_defect != 'nan':
                        cases.append({
                            'complaint': complaint,
                            'actual_defect': actual_defect,
                            'source': 'dataset_1'
                        })
                except Exception as e:
                    continue
        
        # Dataset 2: defeito_reclamado_descricao -> defeito_constatado_descricao
        if self.df2 is not None:
            for _, row in self.df2.iterrows():
                try:
                    complaint = str(row.get('defeito_reclamado_descricao', '') or 
                                  row.get('reclamacao', '') or 
                                  row.get('complaint', ''))
                    
                    actual_defect = str(row.get('defeito_constatado_descricao', '') or 
                                      row.get('defeito_constatado', '') or 
                                      row.get('defect', ''))
                    
                    if complaint and actual_defect and complaint != 'nan' and actual_defect != 'nan':
                        cases.append({
                            'complaint': complaint,
                            'actual_defect': actual_defect,
                            'source': 'dataset_2'
                        })
                except Exception as e:
                    continue
        
        return cases
    
    def _build_vectorstore(self) -> FAISS:
        """Build FAISS vector store from historical cases"""
        documents = []
        
        for case in self.historical_cases:
            # Create document with complaint as content and metadata
            doc = Document(
                page_content=case['complaint'],
                metadata={
                    'actual_defect': case['actual_defect'],
                    'source': case['source']
                }
            )
            documents.append(doc)
        
        # Create FAISS index
        vectorstore = FAISS.from_documents(documents, self.embeddings)
        return vectorstore
    
    def retrieve_similar_cases(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve k most similar historical cases"""
        similar_docs = self.vectorstore.similarity_search(query, k=k)
        
        cases = []
        for doc in similar_docs:
            cases.append({
                'complaint': doc.page_content,
                'actual_defect': doc.metadata['actual_defect'],
                'source': doc.metadata['source']
            })
        
        return cases
    
    def classify_with_rag(
        self, 
        customer_complaint: str, 
        ml_prediction: Optional[Dict] = None,
        top_k: int = 5
    ) -> DefectClassificationResult:
        """
        Classify defect using RAG approach
        
        Args:
            customer_complaint: Customer's complaint text
            ml_prediction: Optional ML model prediction with confidence
            top_k: Number of similar cases to retrieve
            
        Returns:
            DefectClassificationResult with structured classification
        """
        
        # Retrieve similar historical cases
        similar_cases = self.retrieve_similar_cases(customer_complaint, k=top_k)
        
        # Build context from similar cases
        context = self._build_context(similar_cases)
        
        # Build prompt
        prompt = self._build_prompt(customer_complaint, context, ml_prediction)
        
        # Get structured response from LLM
        result = self.structured_llm.invoke(prompt)
        
        return result
    
    def _build_context(self, similar_cases: List[Dict]) -> str:
        """Build context string from similar cases"""
        if not similar_cases:
            return "Nenhum caso similar encontrado no histórico."
        
        context_parts = ["Casos similares do histórico:"]
        for i, case in enumerate(similar_cases, 1):
            context_parts.append(
                f"\n{i}. Reclamação: \"{case['complaint']}\"\n"
                f"   Defeito Real: {case['actual_defect']}"
            )
        
        return "\n".join(context_parts)
    
    def _build_prompt(
        self, 
        complaint: str, 
        context: str, 
        ml_prediction: Optional[Dict] = None
    ) -> str:
        """Build comprehensive prompt for LLM"""
        
        prompt_parts = [
            "Você é um especialista técnico em classificação de defeitos de equipamentos eletrônicos.",
            "",
            context,
            "",
            f"Nova reclamação do cliente:\n\"{complaint}\"",
            ""
        ]
        
        if ml_prediction:
            prompt_parts.append(
                f"O modelo de Machine Learning sugeriu: \"{ml_prediction.get('defect', 'N/A')}\" "
                f"com {ml_prediction.get('confidence', 0)*100:.1f}% de confiança."
            )
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Baseando-se nos casos históricos similares acima, classifique o defeito:",
            "- Crie um código curto (ex: TELA_QUEBRADA, PLACA_CURTO)",
            "- Dê um nome técnico claro",
            "- Liste os termos-chave da reclamação que justificam sua decisão",
            "- Indique seu nível de confiança (0.0 a 1.0)",
            "- Explique brevemente seu raciocínio com base nos casos similares"
        ])
        
        return "\n".join(prompt_parts)
    
    def save_vectorstore(self, path: str = "vectorstore_defeitos"):
        """Save vector store to disk for faster loading"""
        self.vectorstore.save_local(path)
        print(f"✅ Vector store saved to {path}")
    
    @classmethod
    def load_from_disk(cls, vectorstore_path: str = "vectorstore_defeitos"):
        """Load pre-built vector store from disk"""
        instance = cls.__new__(cls)
        
        print("📚 Loading embeddings model...")
        instance.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"🗂️ Loading vector store from {vectorstore_path}...")
        instance.vectorstore = FAISS.load_local(
            vectorstore_path, 
            instance.embeddings,
            allow_dangerous_deserialization=True
        )
        
        print("🤖 Initializing Azure OpenAI...")
        instance.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            temperature=0
        )
        instance.structured_llm = instance.llm.with_structured_output(DefectClassificationResult)
        
        print("✅ RAG system loaded from disk!")
        return instance


# ── Main: Test the RAG system ────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  RAG Defect Classifier - Test")
    print("="*60 + "\n")
    
    # Initialize RAG system
    rag = RAGDefectClassifier()
    
    # Save vector store for future use
    rag.save_vectorstore()
    
    # Test classification
    print("\n" + "="*60)
    print("  Testing Classification")
    print("="*60 + "\n")
    
    test_complaints = [
        "tela quebrada não funciona",
        "celular não liga",
        "bateria não carrega",
        "som não sai do alto falante"
    ]
    
    for complaint in test_complaints:
        print(f"\n🔍 Complaint: \"{complaint}\"")
        print("-" * 60)
        
        try:
            result = rag.classify_with_rag(complaint)
            
            print(f"✅ Defect: {result.defect_name} ({result.defect_code})")
            print(f"📊 Confidence: {result.confidence*100:.1f}%")
            print(f"🔑 Root Cause: {', '.join(result.root_cause)}")
            print(f"💡 Reasoning: {result.reasoning}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✨ RAG system is ready to use!")
    print("="*60)
