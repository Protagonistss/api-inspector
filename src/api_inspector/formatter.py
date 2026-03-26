"""
Output formatter for displaying captured requests.
"""

import json
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import box

from .models import CapturedRequest


class OutputFormatter:
    """Format and display captured requests."""

    def __init__(
        self,
        json_output: bool = False,
        verbose: bool = False,
        no_color: bool = False
    ):
        self.json_output = json_output
        self.verbose = verbose
        self.no_color = no_color
        self.console = Console(no_color=no_color)

    def print_banner(self, host: str, port: int) -> None:
        """Print startup banner."""
        banner = Panel(
            f"[bold green]Proxy running on[/bold green] [cyan]http://{host}:{port}[/cyan]\n\n"
            f"[dim]Configure your system or application to use this proxy to capture requests.[/dim]\n"
            f"[dim]Press Ctrl+C to stop.[/dim]",
            title="[bold blue]API Inspector[/bold blue]",
            border_style="blue",
        )
        self.console.print(banner)
        self.console.print()

    def _get_status_color(self, status_code: Optional[int]) -> str:
        """Get color for status code."""
        if status_code is None:
            return "white"
        if 200 <= status_code < 300:
            return "green"
        if 300 <= status_code < 400:
            return "yellow"
        if 400 <= status_code < 500:
            return "red"
        if status_code >= 500:
            return "bold red"
        return "white"

    def _get_method_color(self, method: str) -> str:
        """Get color for HTTP method."""
        colors = {
            'GET': 'green',
            'POST': 'yellow',
            'PUT': 'blue',
            'PATCH': 'cyan',
            'DELETE': 'red',
            'HEAD': 'magenta',
            'OPTIONS': 'white',
            'WS': 'bright_blue',
        }
        return colors.get(method.upper(), 'white')

    def _format_size(self, size: Optional[int]) -> str:
        """Format size in bytes to human readable."""
        if size is None:
            return "-"
        if size < 1024:
            return f"{size}B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        return f"{size / (1024 * 1024):.1f}MB"

    def _format_body(self, body: Optional[bytes], content_type: Optional[str]) -> str:
        """Format request/response body for display."""
        if body is None:
            return ""

        try:
            text = body.decode('utf-8', errors='replace')
        except:
            return f"<binary data: {len(body)} bytes>"

        # Try to pretty-print JSON
        if content_type and 'json' in content_type.lower():
            try:
                parsed = json.loads(text)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

        # Truncate if too long and not verbose
        if not self.verbose and len(text) > 500:
            return text[:500] + "\n... (truncated, use --verbose for full content)"

        return text

    def _output_json(self, captured: CapturedRequest) -> None:
        """Output request as JSON."""
        data = {
            'timestamp': captured.timestamp.isoformat(),
            'method': captured.method,
            'url': captured.url,
            'host': captured.host,
            'path': captured.path,
            'query_params': captured.query_params,
            'response_status': captured.response_status,
            'response_time_ms': captured.response_time_ms,
            'response_content_type': captured.response_content_type,
            'is_websocket': captured.is_websocket,
        }

        if self.verbose:
            data['request_headers'] = captured.request_headers
            data['response_headers'] = captured.response_headers
            if captured.request_body:
                try:
                    data['request_body'] = captured.request_body.decode('utf-8', errors='replace')
                except:
                    data['request_body'] = f"<binary: {len(captured.request_body)} bytes>"
            if captured.response_body:
                try:
                    data['response_body'] = captured.response_body.decode('utf-8', errors='replace')
                except:
                    data['response_body'] = f"<binary: {len(captured.response_body)} bytes>"

        self.console.print(json.dumps(data, ensure_ascii=False))

    def format_request(self, captured: CapturedRequest) -> None:
        """Format and display a captured HTTP request."""
        if self.json_output:
            self._output_json(captured)
            return

        # Compact table format
        time_str = captured.timestamp.strftime('%H:%M:%S')
        method_colored = f"[{self._get_method_color(captured.method)}]{captured.method}[/{self._get_method_color(captured.method)}]"
        status_colored = f"[{self._get_status_color(captured.response_status)}]{captured.response_status or '-'}[/{self._get_status_color(captured.response_status)}]"
        size = self._format_size(len(captured.response_body) if captured.response_body else None)
        time_ms = f"{captured.response_time_ms:.0f}ms" if captured.response_time_ms else "-"

        # Truncate URL for display
        url_display = captured.url
        if len(url_display) > 60:
            url_display = url_display[:57] + "..."

        self.console.print(
            f"{time_str} | {method_colored} | {url_display} | {status_colored} | {size} | {time_ms}"
        )

        # Verbose output
        if self.verbose:
            self._print_verbose_details(captured)

    def _print_verbose_details(self, captured: CapturedRequest) -> None:
        """Print detailed request/response information."""
        # Request details
        self.console.print(f"\n[bold cyan]Request:[/bold cyan]")
        self.console.print(f"  [dim]Headers:[/dim]")
        for key, value in captured.request_headers.items():
            self.console.print(f"    {key}: {value}")

        if captured.query_params:
            self.console.print(f"  [dim]Query Parameters:[/dim]")
            for key, value in captured.query_params.items():
                self.console.print(f"    {key}: {value}")

        if captured.request_body:
            self.console.print(f"  [dim]Body:[/dim]")
            body_text = self._format_body(captured.request_body, None)
            self.console.print(f"    {body_text[:200]}{'...' if len(body_text) > 200 else ''}")

        # Response details
        if captured.response_status:
            self.console.print(f"\n[bold cyan]Response:[/bold cyan] [{self._get_status_color(captured.response_status)}]{captured.response_status}[/{self._get_status_color(captured.response_status)}]")
            self.console.print(f"  [dim]Headers:[/dim]")
            if captured.response_headers:
                for key, value in captured.response_headers.items():
                    self.console.print(f"    {key}: {value}")

            if captured.response_body:
                self.console.print(f"  [dim]Body:[/dim]")
                body_text = self._format_body(captured.response_body, captured.response_content_type)

                # Syntax highlight JSON
                if captured.response_content_type and 'json' in captured.response_content_type.lower():
                    try:
                        syntax = Syntax(body_text, "json", theme="monokai", line_numbers=False)
                        self.console.print(syntax)
                    except:
                        self.console.print(f"    {body_text[:500]}{'...' if len(body_text) > 500 else ''}")
                else:
                    self.console.print(f"    {body_text[:500]}{'...' if len(body_text) > 500 else ''}")

        self.console.print()  # Empty line for separation

    def format_websocket_message(self, captured: CapturedRequest) -> None:
        """Format and display a WebSocket message."""
        if self.json_output:
            self._output_json(captured)
            return

        time_str = captured.timestamp.strftime('%H:%M:%S')
        method_colored = f"[{self._get_method_color('WS')}]{captured.method}[/{self._get_method_color('WS')}]"

        # Truncate URL for display
        url_display = captured.url
        if len(url_display) > 60:
            url_display = url_display[:57] + "..."

        for msg in captured.websocket_messages:
            direction = "[yellow]→[/yellow]" if msg['from_client'] else "[blue]←[/blue]"
            content = msg['content']
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            if len(str(content)) > 80:
                content = str(content)[:77] + "..."

            self.console.print(
                f"{time_str} | {method_colored} | {url_display} | {direction} {content}"
            )

    def format_websocket_close(self, url: str) -> None:
        """Format WebSocket close event."""
        time_str = datetime.now().strftime('%H:%M:%S')
        self.console.print(f"{time_str} | [dim]WS CLOSED[/dim] | {url}")
