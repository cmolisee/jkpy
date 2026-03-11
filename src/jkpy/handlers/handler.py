from __future__ import annotations

from abc import ABC, abstractmethod

from jkpy.mvc.menu import MenuModel, MenuView


class Handler(ABC):
    """Abstract class for all handlers"""

    def __init__(self) -> None:
        self.next_handler: Handler | None = None

    def set_next(self, handler: Handler) -> Handler:
        """sets the next handler in the chain"""
        self.next_handler = handler
        return handler

    def handle(self, model: MenuModel, view: MenuView) -> None:
        """primary driver for the handler to call the process logic and then invoke the next handler"""
        self.process(model, view)

        if self.next_handler:
            return self.next_handler.handle(model, view)

    @abstractmethod
    def process(self, model: MenuModel, view: MenuView) -> None:
        """Business logic to execute"""
        pass
