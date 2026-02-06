import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    token: str
    log_channel_id: int
    storage_channel_id: int


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class SubscriptionConfig:
    enabled: bool
    channel_ids: List[int]


@dataclass
class StateConfig:
    timeout_seconds: int


@dataclass
class Config:
    bot: BotConfig
    database: DatabaseConfig
    subscription: SubscriptionConfig
    state: StateConfig
    debug: bool = False
    default_language: str = "ar"


def load_config() -> Config:
    channel_ids_raw = os.getenv("SUBSCRIPTION_CHANNEL_IDS", "")
    channel_ids = []
    if channel_ids_raw:
        channel_ids = [int(cid.strip()) for cid in channel_ids_raw.split(",") if cid.strip()]

    return Config(
        bot=BotConfig(
            token=os.getenv("BOT_TOKEN", ""),
            log_channel_id=int(os.getenv("LOG_CHANNEL_ID", "0")),
            storage_channel_id=int(os.getenv("STORAGE_CHANNEL_ID", "0")),
        ),
        database=DatabaseConfig(
            url=os.getenv("DATABASE_URL", ""),
        ),
        subscription=SubscriptionConfig(
            enabled=os.getenv("SUBSCRIPTION_ENABLED", "false").lower() == "true",
            channel_ids=channel_ids,
        ),
        state=StateConfig(
            timeout_seconds=int(os.getenv("STATE_TIMEOUT_SECONDS", "300")),
        ),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        default_language=os.getenv("DEFAULT_LANGUAGE", "ar"),
    )
