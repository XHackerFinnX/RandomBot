from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    POSTGRESQL_USER: SecretStr
    POSTGRESQL_PASSWORD: SecretStr
    POSTGRESQL_HOST: SecretStr
    POSTGRESQL_PORT: SecretStr
    POSTGRESQL_DATABASE: SecretStr
    
    # WEBAPP_URL: str = "https://dqrest-178-236-140-171.ru.tuna.am"
    WEBAPP_URL: str = "https://randomrace.serveo.net"
    
    # WEBHOOK_URL: str = "https://dqrest-178-236-140-171.ru.tuna.am"
    WEBHOOK_URL: str = "https://randomrace.serveo.net"
    WEBHOOK_PATH: str = "/webhook"
    
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
config = Settings()