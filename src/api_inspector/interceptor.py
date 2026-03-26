"""
Interceptor addon for mitmproxy.
"""

import time
from datetime import datetime
from typing import TYPE_CHECKING

from mitmproxy import http

from .filters import RequestFilter
from .formatter import OutputFormatter
from .models import CapturedRequest

if TYPE_CHECKING:
    from mitmproxy.websocket import WebSocketData


class InterceptorAddon:
    """mitmproxy addon to intercept and log HTTP/HTTPS/WebSocket requests."""

    def __init__(
        self,
        request_filter: RequestFilter,
        formatter: OutputFormatter
    ):
        self.request_filter = request_filter
        self.formatter = formatter
        self._request_start_times: dict = {}

    def request(self, flow: http.HTTPFlow) -> None:
        """Called when a request is received."""
        # Store start time for response time calculation
        self._request_start_times[flow.id] = time.time()

        # Build captured request object
        captured = CapturedRequest(
            timestamp=datetime.now(),
            method=flow.request.method,
            url=flow.request.pretty_url,
            host=flow.request.pretty_host,
            path=flow.request.path,
            query_params=dict(flow.request.query) if flow.request.query else {},
            request_headers=dict(flow.request.headers),
            request_body=flow.request.content,
        )

        # Check if this is a websocket upgrade request
        is_websocket_upgrade = (
            flow.request.headers.get("Upgrade", "").lower() == "websocket"
        )

        # Apply URL and method filters
        if not self.request_filter.should_capture_request(
            url=captured.url,
            method=captured.method
        ):
            return

        # Store captured data in flow for use in response handler
        flow._captured_request = captured
        flow._is_websocket_upgrade = is_websocket_upgrade

    def response(self, flow: http.HTTPFlow) -> None:
        """Called when a response is received."""
        if not hasattr(flow, '_captured_request'):
            return

        captured: CapturedRequest = flow._captured_request

        # Calculate response time
        start_time = self._request_start_times.pop(flow.id, None)
        if start_time:
            captured.response_time_ms = (time.time() - start_time) * 1000

        # Update with response data
        captured.response_status = flow.response.status_code
        captured.response_headers = dict(flow.response.headers)
        captured.response_body = flow.response.content

        # Extract content type
        content_type = flow.response.headers.get("Content-Type", "")
        captured.response_content_type = content_type.split(";")[0].strip() if content_type else None

        # Check if this was a WebSocket upgrade
        if hasattr(flow, '_is_websocket_upgrade') and flow._is_websocket_upgrade:
            captured.is_websocket = True

        # Apply status code and content type filters
        if not self.request_filter.should_capture_response(
            status_code=captured.response_status,
            content_type=captured.response_content_type
        ):
            return

        # Format and output
        self.formatter.format_request(captured)

        # Format and output
        self.formatter.format_websocket_close(flow.request.pretty_url)

        """Called when a WebSocket message is received or sent."""
        if not flow.websocket:
            return

        ws: WebSocketData = flow.websocket

        # Get the most recent message
        if not ws.messages:
            return

        message = ws.messages[-1]

        # Build captured request for WebSocket message
        captured = CapturedRequest(
            timestamp=datetime.now(),
            method="WS",
            url=flow.request.pretty_url,
            host=flow.request.pretty_host,
            path=flow.request.path,
            query_params={},
            request_headers={},
            is_websocket=True,
            websocket_messages=[{
                'timestamp': datetime.fromtimestamp(message.timestamp),
                'from_client': message.from_client,
                'content': message.content,
                'type': message.type.value if hasattr(message.type, 'value') else str(message.type),
            }]
        )

        # Apply URL filter
        if not self.request_filter.should_capture_request(
            url=captured.url,
            method="WS"
        ):
            return

        # Format and output
        self.formatter.format_websocket_message(captured)

    def websocket_end(self, flow: http.HTTPFlow) -> None:
        """Called when a WebSocket connection is closed."""
        if self.formatter.verbose and flow.request:
            self.formatter.format_websocket_close(flow.request.pretty_url)
