from typing import Type

from src.notify.webhook import WebhookNotifier


class NotifierFactory:
    _notifiers = {
        "webhook": WebhookNotifier,
    }

    @classmethod
    def get_notifier(self, notifier_type: str) -> Type[WebhookNotifier]:
        return self._notifiers[notifier_type]
