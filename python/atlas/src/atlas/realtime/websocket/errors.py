class WebSocketError(Exception):
    pass


class WebSocketProtocolError(WebSocketError):
    pass


class SubscriptionLimitExceeded(WebSocketError):
    pass
