"""
Backend Configuration
Environment-aware settings for development and production
"""

import os
from typing import List

class Config:
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    IS_DEVELOPMENT = ENVIRONMENT == "development"
    IS_PRODUCTION = ENVIRONMENT == "production"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins based on environment"""
        if cls.IS_PRODUCTION:
            return [
                cls.FRONTEND_URL,
                "https://your-app.vercel.app",  # Replace with your actual Vercel URL
                "https://*.vercel.app"  # All Vercel preview deployments
            ]
        else:
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000", 
                cls.FRONTEND_URL
            ]
    
    @classmethod
    def get_config_info(cls) -> dict:
        """Get configuration information for debugging"""
        return {
            "environment": cls.ENVIRONMENT,
            "is_development": cls.IS_DEVELOPMENT,
            "is_production": cls.IS_PRODUCTION,
            "frontend_url": cls.FRONTEND_URL,
            "cors_origins": cls.get_cors_origins(),
            "openai_configured": bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "your_openai_api_key_here")
        }

# Create global config instance
config = Config() 