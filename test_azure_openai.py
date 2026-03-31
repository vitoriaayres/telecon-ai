"""
Test script to verify Azure OpenAI configuration
Run this AFTER you've filled in .env with your Azure credentials
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load .env file
load_dotenv()

def test_azure_openai_connection():
    """Test if Azure OpenAI is configured correctly"""
    
    print("🔍 Checking Azure OpenAI configuration...\n")
    
    # Check environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    print(f"✓ Endpoint: {endpoint}")
    print(f"✓ Deployment: {deployment}")
    print(f"✓ API Version: {api_version}")
    print(f"✓ API Key: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'NOT SET'}\n")
    
    if not endpoint or not api_key:
        print("❌ ERROR: Azure OpenAI credentials not found!")
        print("👉 Please copy .env.azure_template to .env and fill in your credentials")
        print("   See AZURE_OPENAI_SETUP.md for step-by-step guide")
        return False
    
    try:
        print("🚀 Testing connection to Azure OpenAI...\n")
        
        # Initialize client
        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment_name=deployment,
            temperature=0
        )
        
        # Make a simple test call
        response = llm.invoke("Responda apenas: OK")
        
        print("✅ SUCCESS! Azure OpenAI is working!")
        print(f"📩 Response: {response.content}\n")
        
        # Test with defect classification task
        print("🧪 Testing defect classification task...\n")
        
        test_message = """
        Você é um classificador de defeitos técnicos.
        
        Cliente disse: "o celular caiu e a tela quebrou"
        
        Qual é o defeito? Responda em uma frase curta.
        """
        
        response = llm.invoke(test_message)
        print(f"🔧 Defect Classification: {response.content}\n")
        
        print("=" * 60)
        print("✅ All tests passed! Azure OpenAI is ready to use.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}\n")
        print("Common issues:")
        print("  1. Check endpoint URL format: https://YOUR-RESOURCE.openai.azure.com/")
        print("  2. Verify deployment name matches Azure OpenAI Studio")
        print("  3. Ensure API key is correct (regenerate if needed)")
        print("  4. Wait 2-3 minutes if you just created the deployment")
        print("\n👉 See AZURE_OPENAI_SETUP.md for troubleshooting guide")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Azure OpenAI Connection Test")
    print("=" * 60 + "\n")
    
    success = test_azure_openai_connection()
    
    if success:
        print("\n✨ Next steps:")
        print("  1. Run: python classificador.py (test structured output)")
        print("  2. Integrate with api.py for full ML + LLM system")
        print("  3. Implement RAG with your datasets")
    else:
        print("\n🔧 Please fix the issues above and try again")
        print("   Run: python test_azure_openai.py")
