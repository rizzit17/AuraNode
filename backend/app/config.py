import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AuraNode GraphRAG Engine"
    API_ENV: str = "development"
    API_PORT: int = 8000
    
    # Groq Settings
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    
    # Neo4j Settings
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    
    # Supabase / Vector DB Settings
    SUPABASE_DB_URL: str = ""
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,*"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
