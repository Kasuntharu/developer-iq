from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GITHUB_USERNAME: str
    GITHUB_ACCESS_TOKEN: str
    AWS_REGION: str
    AWS_SECRET_KEY: str
    AWS_ACCESS_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()