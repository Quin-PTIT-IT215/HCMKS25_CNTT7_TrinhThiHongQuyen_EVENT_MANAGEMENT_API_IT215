from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = 'EVENT MANAGEMENT API'
    APP_VERSION: str = '1.0.0'
    APP_DECRIPTION: str = 'EVENT MANAGEMENT API'

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINITES: int = 30

    ALLOWED_ORIGINS = list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file = '.env',
        env_file_encoding= 'utf-8'
    )

settings = Settings()