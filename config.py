import os

SECRET_KEY = "jdkshfjdhjskhiuyxvbcseyvyfbhjvbysdgbbpoewqruipoueowbc3jkb345646bjkbkjdsa7878mndsa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20  # 20 minutes

HARDCODED_USERNAME = "anurag"
HARDCODED_PASSWORD = "password123"

CACHE_BACKEND = "memory"

REDIS_URL = "redis://localhost:6379/0"
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
LOG_LEVEL = "INFO"


OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")