from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
	host: str = Field(default="localhost", alias="DB_HOST")
	port: int = Field(default=5432, alias="DB_PORT")
	user: str = Field(default="postgres", alias="DB_USER")
	password: SecretStr = Field(alias="DB_PASS")
	name: str = Field(alias="DB_NAME")
	use_logging: bool = Field(default=False, alias="DB_USE_LOGGING")
	pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
	max_overflow: int = Field(default=5, alias="DB_MAX_OVERFLOW")

	def get_url(self):
		return (f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@"
				f"{self.host}:{self.port}/{self.name}")

	model_config = SettingsConfigDict(
		env_prefix="DB_",
		env_file="settings/.env",
		extra="ignore"
	)


class JWTConfig(BaseSettings):
	secret_key: SecretStr = Field(alias="JWT_SECRET_KEY")
	algorithm: str = Field(alias="JWT_ALGORITHM", default="HS256")
	access_token_expire_minutes: int = Field(alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
	refresh_token_expire_days: int = Field(alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=7)

	model_config = SettingsConfigDict(
		env_prefix="JWT_",
		env_file="settings/.env",
		extra="ignore"
	)


class Settings(BaseSettings):
	db_cfg: DBConfig = Field(default_factory=DBConfig)
	jwt_cfg: JWTConfig = Field(default_factory=JWTConfig)

	class Config:
		env_file = "settings/.env"
		extra = "ignore"


settings = Settings()
