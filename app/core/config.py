from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool
    project_name: str
    api_prefix: str
    db_url: str
    secret_key: str
    payment_secret_key: str
    payment_project_id: str
    payment_mode: int

    class Config:
        env_file = ".env"


settings = Settings()  # pyright: ignore[reportCallIssue,reportGeneralTypeIssues]
