from typing import Protocol


class Broker(Protocol):
    def connect(self) -> None: ...


class Publisher(Protocol):
    def publish(self, queue_name: str, message: dict) -> None: ...

    def __getattr__(self, name):
        return self.publish(name)
