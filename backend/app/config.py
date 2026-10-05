from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    LLM_MODEL: str = "gemini-2.5-flash"
    DATABASE_URL: str = "sqlite:///./careerguide.db"
    FRONTEND_URL: str = "http://localhost:5173"
    CHROMA_DIR: str = "./chroma_db"
    KNOWLEDGE_DIR: str = "../knowledge_base"

    class Config:
        env_file = ".env"


settings = Settings()
