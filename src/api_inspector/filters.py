"""
Request filtering functionality.
"""

import re
import fnmatch
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class RequestFilter:
    """Configuration for filtering captured requests."""

    url_patterns: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    status_codes: Optional[List[int]] = None
    content_types: Optional[List[str]] = None

    def _match_pattern(self, value: str, pattern: str) -> bool:
        """Match a value against a pattern (supports wildcards and regex)."""
        # Try glob pattern first (e.g., api.*.com)
        if fnmatch.fnmatch(value, pattern):
            return True

        # Try as regex if it looks like one
        try:
            if re.search(pattern, value):
                return True
        except re.error:
            pass

        return False

    def should_capture_request(
        self,
        url: str,
        method: str
    ) -> bool:
        """Check if a request should be captured based on URL and method filters.

        Args:
            url: The request URL
            method: The HTTP method

        Returns:
            True if the request should be captured
        """
        # URL filter
        if self.url_patterns:
            url_matched = any(
                self._match_pattern(url, pattern)
                for pattern in self.url_patterns
            )
            if not url_matched:
                return False

        # Method filter
        if self.methods:
            if method.upper() not in [m.upper() for m in self.methods]:
                return False

        return True

    def should_capture_response(
        self,
        status_code: Optional[int],
        content_type: Optional[str]
    ) -> bool:
        """Check if a response should be captured based on status code and content type filters.

        Args:
            status_code: The response status code
            content_type: The response content type

        Returns:
            True if the response should be captured
        """
        # Status code filter
        if self.status_codes:
            if status_code not in self.status_codes:
                return False

        # Content type filter
        if self.content_types:
            if not content_type:
                return False

            content_type_lower = content_type.lower()
            content_type_matched = any(
                ct.lower() in content_type_lower
                for ct in self.content_types
            )
            if not content_type_matched:
                return False

        return True
