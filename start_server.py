#!/usr/bin/env python3
"""
Backend server başlatma script'i
"""

import subprocess
import sys
import os

def check_requirements():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et"""
    try:
        import fastapi
        import uvicorn
        import openai
        import dotenv
        print("✅ Tüm gerekli paketler yüklü")
        return True
    except ImportError as e:
        print(f"❌ Eksik paket: {e}")
        print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın")
        return False

def check_env_file():
    """Environment dosyasının varlığını kontrol et"""
    if not os.path.exists('.env'):
        print("❌ .env dosyası bulunamadı")
        print("Lütfen .env dosyasını oluşturun ve OpenAI API key'inizi ekleyin")
        return False
    
    # Check if OPENAI_API_KEY is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_openai_api_key_here' in content:
            print("⚠️  OpenAI API key henüz ayarlanmamış")
            print("Lütfen .env dosyasındaki OPENAI_API_KEY'i güncelleyin")
            return False
    
    print("✅ Environment dosyası hazır")
    return True

def start_server():
    """Server'ı başlat"""
    print("🚀 Backend server başlatılıyor...")
    print("📍 Server: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    print("🔄 Hot reload etkin")
    print("\n" + "="*50 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server kapatıldı")

if __name__ == "__main__":
    print("🔧 Emsal Zeka Backend Server")
    print("="*50)
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        print("\n📝 Devam etmek için .env dosyasını düzenleyin")
        choice = input("Yine de devam etmek istiyor musunuz? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(1)
    
    start_server() 