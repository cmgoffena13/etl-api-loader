from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseNotifier(ABC):
    @abstractmethod
    def _create_message(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass
