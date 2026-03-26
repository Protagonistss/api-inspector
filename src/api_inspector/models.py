"""
Data models for captured requests.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CapturedRequest:
    """Data class to store captured request information."""
    timestamp: datetime
    method: str
    url: str
    host: str
    path: str
    query_params: dict
    request_headers: dict
    request_body: Optional[bytes] = None
    response_status: Optional[int] = None
    response_headers: Optional[dict] = None
    response_body: Optional[bytes] = None
    response_content_type: Optional[str] = None
    response_time_ms: Optional[float] = None
    is_websocket: bool = False
    websocket_messages: list = field(default_factory=list)
