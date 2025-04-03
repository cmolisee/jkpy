class JiraHandler:
    """Abstract class for all handlers.
    """
    def __init__(self, nxt=None):
        """Initializes the handler object.

        Args:
            nxt (_type_, optional): _description_. Defaults to None.
        """
        self._next_handler=nxt;

    def handle(self, request):
        """Main driver function for the handler object.

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """
        if self._next_handler:
            self._next_handler.handle(request)
        return None
