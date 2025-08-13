from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    allowed_file_types: str
    max_file_size: int
    allowed_origins: str  # Comma-separated string
    together_api_key: str

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.allowed_origins.split(",")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()