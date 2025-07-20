# Emsal Zeka Backend

Python FastAPI backend server with OpenAI integration for legal case search.

## Kurulum

1. **Python Paketlerini Yükle:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Environment Variables:**
`.env` dosyası oluşturun:
```
OPENAI_API_KEY=your_openai_api_key_here
FRONTEND_URL=http://localhost:3000
```

3. **Server'ı Başlat:**
```bash
python start_server.py
```

Ya da doğrudan:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /` - Ana sayfa
- `GET /health` - Sağlık kontrolü  
- `POST /api/search` - Ana arama endpoint'i

## API Docs

Server çalışırken: http://localhost:8000/docs

## Özellikler

- ✅ FastAPI ile RESTful API
- ✅ OpenAI GPT-3.5-turbo entegrasyonu
- ✅ CORS desteği frontend için
- ✅ Türkçe hukuki sorgular için optimize edilmiş promptlar
- ✅ Error handling ve logging
- ✅ Pydantic data validation 