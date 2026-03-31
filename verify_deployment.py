#!/usr/bin/env python3
"""
🔍 Complete Deployment Verification Script
Tests local setup, backend API, and frontend deployment
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("1. Checking Environment Configuration")
    
    if not Path('.env').exists():
        print_error(".env file not found!")
        return False
    
    print_success(".env file exists")
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var} is set")
        else:
            print_error(f"{var} is missing!")
            missing.append(var)
    
    return len(missing) == 0

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print_header("2. Checking Python Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'scikit-learn',
        'pandas',
        'joblib',
        'openai',
        'langchain',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    return all_installed

def check_model_files():
    """Check if ML model files exist"""
    print_header("3. Checking ML Model Files")
    
    model_files = [
        'classificador_defeitos.pkl',
        'classificador_defeitos_classes.pkl',
        'classificador_semantico.pkl'
    ]
    
    found = 0
    for file in model_files:
        if Path(file).exists():
            size_mb = Path(file).stat().st_size / (1024 * 1024)
            print_success(f"{file} exists ({size_mb:.2f} MB)")
            found += 1
        else:
            print_warning(f"{file} not found (will be created on first run)")
    
    return found > 0

def check_dataset():
    """Check if dataset files exist"""
    print_header("4. Checking Dataset Files")
    
    dataset_path = Path('DATASET')
    if not dataset_path.exists():
        print_error("DATASET folder not found!")
        return False
    
    print_success("DATASET folder exists")
    
    csv_files = list(dataset_path.glob('*.csv'))
    if csv_files:
        print_success(f"Found {len(csv_files)} CSV file(s)")
        for csv in csv_files[:3]:  # Show first 3
            size_mb = csv.stat().st_size / (1024 * 1024)
            print_info(f"  - {csv.name} ({size_mb:.2f} MB)")
        return True
    else:
        print_warning("No CSV files found in DATASET folder")
        return False

def test_backend_local():
    """Test if backend API is running locally"""
    print_header("5. Testing Local Backend API")
    
    endpoints = [
        ('http://localhost:8000/health', 'Health Check'),
        ('http://localhost:8000/docs', 'API Documentation'),
    ]
    
    backend_running = False
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{name}: {url}")
                backend_running = True
            else:
                print_error(f"{name} returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_warning(f"{name}: Not running (expected if not started)")
        except Exception as e:
            print_error(f"{name}: Error - {str(e)}")
    
    return backend_running

def test_backend_azure():
    """Test Azure backend deployment"""
    print_header("6. Testing Azure Backend Deployment")
    
    azure_url = "http://4.228.41.39:8000"
    
    try:
        print_info(f"Testing {azure_url}/health")
        response = requests.get(f"{azure_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Azure backend is LIVE!")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Azure backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Azure backend!")
        print_info("Make sure the Azure Container Instance is running")
        return False
    except Exception as e:
        print_error(f"Error testing Azure backend: {str(e)}")
        return False

def test_predict_endpoint():
    """Test the /predict endpoint with sample data"""
    print_header("7. Testing Predict Endpoint")
    
    azure_url = "http://4.228.41.39:8000"
    
    test_data = {
        "texto_cliente": "celular não liga tela preta"
    }
    
    try:
        print_info(f"Sending test prediction: '{test_data['texto_cliente']}'")
        response = requests.post(
            f"{azure_url}/predict",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Prediction successful!")
            print_info(f"Results: {len(data.get('resultados', []))} predictions")
            
            if data.get('resultados'):
                top = data['resultados'][0]
                print_info(f"Top prediction: {top.get('defeito_sugerido')} ({top.get('confianca_pct')}%)")
            
            return True
        else:
            print_error(f"Prediction failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error testing prediction: {str(e)}")
        return False

def check_vercel_frontend():
    """Check Vercel frontend deployment"""
    print_header("8. Checking Vercel Frontend")
    
    vercel_url = "https://telecontrol-ai.vercel.app"
    
    try:
        print_info(f"Testing {vercel_url}")
        response = requests.get(vercel_url, timeout=10)
        
        if response.status_code == 200:
            print_success("Vercel frontend is LIVE!")
            print_info(f"URL: {vercel_url}")
            return True
        else:
            print_warning(f"Vercel returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking Vercel: {str(e)}")
        return False

def check_frontend_config():
    """Check frontend configuration"""
    print_header("9. Checking Frontend Configuration")
    
    frontend_path = Path('telecon-ai')
    if not frontend_path.exists():
        print_error("Frontend folder 'telecon-ai' not found!")
        return False
    
    print_success("Frontend folder exists")
    
    # Check package.json
    package_json = frontend_path / 'package.json'
    if package_json.exists():
        print_success("package.json exists")
    else:
        print_error("package.json not found!")
        return False
    
    # Check .env.local
    env_local = frontend_path / '.env.local'
    if env_local.exists():
        print_success(".env.local exists")
        with open(env_local) as f:
            content = f.read()
            if 'BACKEND_URL' in content or 'API_URL' in content:
                print_success("Backend URL is configured")
            else:
                print_warning("Backend URL might not be configured")
    else:
        print_warning(".env.local not found")
    
    return True

def print_summary(results):
    """Print summary of all checks"""
    print_header("📊 VERIFICATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, status in results.items():
        if status:
            print_success(check)
        else:
            print_error(check)
    
    print(f"\n{BLUE}{'─'*60}{RESET}")
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print(f"{GREEN}🎉 ALL CHECKS PASSED! ({passed}/{total}){RESET}")
        print(f"{GREEN}Your deployment is ready!{RESET}")
    elif percentage >= 75:
        print(f"{YELLOW}⚠️  MOSTLY WORKING ({passed}/{total}){RESET}")
        print(f"{YELLOW}Some components need attention{RESET}")
    else:
        print(f"{RED}❌ NEEDS WORK ({passed}/{total}){RESET}")
        print(f"{RED}Several components need fixing{RESET}")
    
    print(f"{BLUE}{'─'*60}{RESET}\n")

def main():
    """Run all verification checks"""
    print(f"{GREEN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     🚀 TELECONTROL DEPLOYMENT VERIFICATION TOOL 🚀       ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    results = {
        "Environment Configuration": check_env_file(),
        "Python Dependencies": check_python_dependencies(),
        "ML Model Files": check_model_files(),
        "Dataset Files": check_dataset(),
        "Local Backend": test_backend_local(),
        "Azure Backend": test_backend_azure(),
        "Predict Endpoint": test_predict_endpoint(),
        "Vercel Frontend": check_vercel_frontend(),
        "Frontend Configuration": check_frontend_config(),
    }
    
    print_summary(results)
    
    # Next steps
    if not results["Azure Backend"]:
        print_info("To start Azure backend, check Azure Portal Container Instances")
    
    if not results["Local Backend"]:
        print_info("To start local backend: uvicorn api:app --reload")
    
    if not results["Vercel Frontend"]:
        print_info("To deploy frontend: cd telecon-ai && vercel --prod")

if __name__ == "__main__":
    main()
