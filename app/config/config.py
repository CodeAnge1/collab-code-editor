from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
	model_config = SettingsConfigDict(env_file="settings/.env")


class DBConfig(ConfigBase):
	host: str = 'localhost'
	port: int = 5432
	user: str
	password: SecretStr
	name: str
	use_logging: bool = False
	pool_size: int = 10
	max_overflow: int = 5

	def get_url(self):
		return (f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@"
				f"{self.host}:{self.port}/{self.name}")


class Settings(BaseSettings):
	db_cfg: DBConfig = Field(default_factory=DBConfig)


settings = Settings()
