from __future__ import annotations

from jkpy.handlers.excel_output_handler import ExcelOutputHandler
from jkpy.handlers.filter import Filter
from jkpy.handlers.handler import Handler
from jkpy.handlers.metrics import Metrics
from jkpy.handlers.normalize import Normalize
from jkpy.handlers.request_accounts import RequestAccounts
from jkpy.handlers.request_issues import RequestIssues
from jkpy.handlers.validate import Validate


class Handlers:
    """Class for managing chain of responsibility"""

    @classmethod
    def create_chain(cls) -> Handler:
        """Create chain from handlers"""
        handlers = {
            0: RequestIssues(),
            1: RequestAccounts(),
            2: Normalize(),
            3: Validate(),
            4: Filter(),
            5: Metrics(),
            6: ExcelOutputHandler(),
        }

        chain = handlers[0]
        chain.set_next(handlers[1]).set_next(handlers[2]).set_next(handlers[3]).set_next(
            handlers[4]
        ).set_next(handlers[5]).set_next(handlers[6])

        return chain


__all__ = ["Handlers"]
