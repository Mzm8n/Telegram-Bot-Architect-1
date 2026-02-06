import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


@dataclass
class UserState:
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    previous_state: Optional[str] = None


class StateService:
    def __init__(self, timeout_seconds: int = 300):
        self._states: Dict[int, UserState] = {}
        self._timeout = timeout_seconds

    def get_state(self, user_id: int) -> Optional[UserState]:
        state = self._states.get(user_id)
        if state is None:
            return None

        if time.time() - state.created_at > self._timeout:
            self.clear_state(user_id)
            logger.info(LogMessages.STATE_EXPIRED.format(user_id=user_id))
            return None

        return state

    def set_state(self, user_id: int, state_name: str, data: Optional[Dict[str, Any]] = None) -> UserState:
        current = self._states.get(user_id)
        previous = current.name if current else None

        new_state = UserState(
            name=state_name,
            data=data or {},
            previous_state=previous,
        )
        self._states[user_id] = new_state
        logger.debug(LogMessages.STATE_SET.format(user_id=user_id, state=state_name))
        return new_state

    def clear_state(self, user_id: int) -> None:
        if user_id in self._states:
            del self._states[user_id]
            logger.debug(LogMessages.STATE_CLEARED.format(user_id=user_id))

    def go_back(self, user_id: int) -> Optional[str]:
        current = self._states.get(user_id)
        if current is None:
            return None

        previous = current.previous_state
        if previous is None:
            self.clear_state(user_id)
            return None

        self._states[user_id] = UserState(name=previous)
        return previous

    def has_state(self, user_id: int) -> bool:
        return self.get_state(user_id) is not None

    def get_state_data(self, user_id: int, key: str, default: Any = None) -> Any:
        state = self.get_state(user_id)
        if state is None:
            return default
        return state.data.get(key, default)

    def update_state_data(self, user_id: int, key: str, value: Any) -> None:
        state = self.get_state(user_id)
        if state is not None:
            state.data[key] = value

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [
            uid for uid, state in self._states.items()
            if now - state.created_at > self._timeout
        ]
        for uid in expired:
            del self._states[uid]

        if expired:
            logger.info(LogMessages.STATES_CLEANUP.format(count=len(expired)))
        return len(expired)


state_service: Optional[StateService] = None


def get_state_service() -> StateService:
    from bot.core.constants import ErrorMessages
    if state_service is None:
        raise RuntimeError(ErrorMessages.STATE_NOT_INITIALIZED)
    return state_service


def init_state_service(timeout_seconds: int = 300) -> StateService:
    global state_service
    state_service = StateService(timeout_seconds=timeout_seconds)
    return state_service
