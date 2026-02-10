from __future__ import annotations
from typing import Protocol
from jkpy.configuration import ConfigurationType

class BaseHandler(Protocol):
    """
    Interface for all other Handlers
    """
    _next_handler: BaseHandler = None
    
    def set_next(self, handler: BaseHandler) -> BaseHandler:
        """
        Sets the next Handler in the chain

        :param handler: The next handler instance
        :type handler: BaseHandler
        :return: The next handler instance
        :rtype: BaseHandler
        """
        self._next_handler = handler
        return handler

    def handle(self, request: ConfigurationType) -> None:
        """
        Business logic of the Handler

        :param request: Dict with all data passed in the chain
        :type request: Configuration
        """
        if self._next_handler:
            return self._next_handler.handle(request)

        return None
