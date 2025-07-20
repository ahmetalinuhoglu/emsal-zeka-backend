from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging
import traceback
from config import config

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Emsal Zeka Backend", version="1.0.0")

# CORS configuration using config
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

# Data models
class SearchRequest(BaseModel):
    query: str
    detailedQuery: str = ""
    filters: Optional[Dict[str, Any]] = {}
    page: int = 1
    limit: int = 10

class Decision(BaseModel):
    id: str
    title: str
    summary: str
    fullText: Optional[str] = None
    date: str
    daire: str
    category: str
    keywords: List[str]
    relevanceScore: Optional[float] = None

class SearchResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Mock data - Bu gerçek veri tabanından gelecek
MOCK_DECISIONS = [
    {
        "id": "1",
        "title": "Yargıtay 4. Hukuk Dairesi - 2024/1542",
        "summary": "Trafik kazasından doğan maddi ve manevi tazminat talebinin değerlendirilmesi, kusur oranının belirlenmesi.",
        "date": "2024-03-15",
        "daire": "4. Hukuk Dairesi",
        "category": "Tazminat",
        "keywords": ["Trafik Kazası", "Tazminat", "Kusur", "Maddi Zarar"],
        "relevanceScore": 0.95
    },
    {
        "id": "2",
        "title": "Yargıtay 2. Hukuk Dairesi - 2024/891",
        "summary": "Sigorta şirketi aleyhine açılan tazminat davasında, sigorta poliçesi kapsamının belirlenmesi.",
        "date": "2024-03-12",
        "daire": "2. Hukuk Dairesi",
        "category": "Sigorta",
        "keywords": ["Sigorta", "Poliçe", "Tazminat", "Teminat"],
        "relevanceScore": 0.87
    }
]

@app.get("/")
async def root():
    return {"message": "Emsal Zeka Backend API"}

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for Railway deployment
    """
    try:
        # Simple health check that doesn't depend on external services
        return {
            "status": "healthy", 
            "message": "Backend is running",
            "timestamp": "2024-07-21",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        }

@app.get("/debug")
async def debug_info():
    """
    Debug endpoint - configuration and connectivity check
    """
    debug_info = {
        "config": config.get_config_info(),
        "openai_client_status": "initialized" if client else "not_initialized",
        "mock_data_count": len(MOCK_DECISIONS),
        "environment_vars": {
            "OPENAI_API_KEY_SET": bool(os.getenv("OPENAI_API_KEY")),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
            "FRONTEND_URL": os.getenv("FRONTEND_URL", "not_set")
        }
    }
    
    # Test OpenAI connection if available
    if client and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            # Simple test request
            test_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            debug_info["openai_test"] = "success"
            logger.info("OpenAI API test successful")
        except Exception as e:
            debug_info["openai_test"] = f"failed: {str(e)}"
            logger.error(f"OpenAI API test failed: {str(e)}")
    else:
        debug_info["openai_test"] = "skipped (no valid API key)"
    
    return debug_info

async def get_llm_response(user_query: str, detailed_query: str) -> str:
    """
    LLM'den cevap almak için OpenAI API'yi kullanır
    """
    if not client:
        logger.error("OpenAI client is not initialized")
        raise HTTPException(status_code=500, detail="OpenAI client is not configured properly")
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        logger.error("OpenAI API key is not configured")
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")
    
    try:
        logger.info(f"Making LLM request for query: {user_query[:50]}...")
        
        # Prompt hazırlığı - Türkçe hukuki sorular için optimize edilmiş
        system_prompt = """Sen Türkiye hukuku konusunda uzman bir hukuk asistanısın. 
        Kullanıcının sorularını analiz ederek en uygun Yargıtay emsal kararlarını bulmasına yardım ediyorsun.
        
        Görevin:
        1. Kullanıcının sorgusunu analiz et
        2. Hangi hukuki konularda arama yapılması gerektiğini belirle
        3. İlgili anahtar kelimeleri ve hukuki kavramları öner
        4. Sorguya en uygun emsal kararları bul ve açıkla
        
        Her zaman Türkçe yanıt ver ve hukuki terimlerı doğru kullan."""
        
        user_message = f"""
        Kullanıcı Sorgusu: {user_query}
        {f'Detaylı Açıklama: {detailed_query}' if detailed_query else ''}
        
        Bu sorguya en uygun emsal kararları bul ve açıkla.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        logger.info("LLM response received successfully")
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM API Error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"LLM API Error: {str(e)}")

@app.post("/api/search", response_model=SearchResponse)
async def search_decisions(request: SearchRequest):
    """
    Ana arama endpoint'i - LLM entegrasyonu ile
    """
    try:
        logger.info(f"Search request received: {request.query}")
        logger.info(f"Request details - Page: {request.page}, Limit: {request.limit}")
        
        # Validate request
        if not request.query or len(request.query.strip()) == 0:
            logger.warning("Empty query received")
            return SearchResponse(
                success=False,
                error="Arama sorgusu boş olamaz"
            )
        
        # LLM'den analiz ve öneriler al
        try:
            logger.info("Getting LLM response...")
            llm_response = await get_llm_response(request.query, request.detailedQuery)
            logger.info("LLM response received successfully")
        except Exception as llm_error:
            logger.error(f"LLM request failed: {str(llm_error)}")
            # Continue with search even if LLM fails
            llm_response = f"LLM analizi şu anda kullanılamıyor: {str(llm_error)}"
        
        # Basit arama algoritması (gerçek implementasyonda daha gelişmiş olacak)
        logger.info("Performing search on mock data...")
        results = []
        for decision in MOCK_DECISIONS:
            # Basit keyword matching
            if (request.query.lower() in decision["title"].lower() or 
                request.query.lower() in decision["summary"].lower() or
                any(keyword.lower() in request.query.lower() for keyword in decision["keywords"])):
                results.append(decision)
        
        logger.info(f"Found {len(results)} matching results")
        
        # Pagination
        start_index = (request.page - 1) * request.limit
        end_index = start_index + request.limit
        paginated_results = results[start_index:end_index]
        
        logger.info(f"Returning {len(paginated_results)} results for page {request.page}")
        
        return SearchResponse(
            success=True,
            data={
                "results": paginated_results,
                "totalResults": len(results),
                "currentPage": request.page,
                "totalPages": (len(results) + request.limit - 1) // request.limit,
                "hasMore": end_index < len(results),
                "llm_analysis": llm_response  # LLM analizini de döndürüyoruz
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in search: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return SearchResponse(
            success=False,
            error=f"Arama sırasında beklenmeyen hata oluştu: {str(e)} | Detay: {type(e).__name__}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 