from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView

class Handler(ABC):
    def __init__(self):
        self.next_handler: Optional[Handler] = None
    
    def set_next(self, handler: "Handler") -> "Handler":
        self.next_handler = handler
        return handler

    def handle(self, model: MenuModel, view: MenuView) -> None:
        self.process(model, view)
        
        if self.next_handler:
            return self.next_handler.handle(model, view)
    
    @abstractmethod
    def process(self, model: MenuModel, view: MenuView) -> None:
        pass
