import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    token: str


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class Config:
    bot: BotConfig
    database: DatabaseConfig
    debug: bool = False


def load_config() -> Config:
    return Config(
        bot=BotConfig(
            token=os.getenv("BOT_TOKEN", ""),
        ),
        database=DatabaseConfig(
            url=os.getenv("DATABASE_URL", ""),
        ),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
