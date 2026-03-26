"""
Proxy server implementation using mitmproxy.
"""

import asyncio
import signal
from typing import Optional

from mitmproxy import master
from mitmproxy import options
from .interceptor import InterceptorAddon
from .filters import RequestFilter
from .formatter import OutputFormatter
from .models import CapturedRequest


class ProxyServer:
    """Proxy server implementation."""

    def __init__(
        self,
        host: str,
        port: int,
        request_filter: RequestFilter,
        formatter: OutputFormatter
    ):
        self.host = host
        self.port = port
        self.request_filter = request_filter
        self.formatter = formatter
        self._master: Optional[master.Master] = None
        self._request_start_times: dict = {}
        self._shutdown_event: Optional[asyncio.Event] = None

        self._task: Optional[asyncio.Task] = None

    def _setup(self) -> None:
        """Set up the proxy server."""
        opts = options.Options(
            listen_host=self.host,
            listen_port=self.port,
        )

        # Create the master
        self._master = master.Master(opts)

        self._master.addons.add(InterceptorAddon(
            self.request_filter,
            self.formatter
        ))

        # Set up shutdown event
        self._shutdown_event = asyncio.Event()

    async def _run(self) -> None:
        """Run the proxy server asynchronously."""
        try:
            await self._master.run()
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        finally:
            if self._shutdown_event:
                self._shutdown_event.set()

    async def shutdown(self) -> None:
        """Shutdown the proxy server."""
        if self._shutdown_event:
            self._shutdown_event.set()
        if self._master:
            await self._master.done()


def stop(self) -> None:
        """Stop the proxy server."""
        if self._task:
            self._task.cancel()
        if self._shutdown_event:
            self._shutdown_event.set()


def run(self) -> None:
        """Run the proxy server synchronously (blocking)."""
        self._setup()

        loop = asyncio.get_running_loop()

        self._shutdown_event.clear()

        self._task = loop.create_task(
            self._run(),
            name="api-inspector-proxy"
        )

        try:
            loop.run_until_complete()
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.stop()
            print("Proxy stopped")
        finally:
            self.shutdown()


def start_proxy(
    host: str,
    port: int,
    request_filter: RequestFilter,
    formatter: OutputFormatter
) -> None:
    """Start the mitmproxy server with the given configuration.

    This is a synchronous version that runs the proxy in the current thread.
    """
    server = ProxyServer(
        host=host,
        port=port,
        request_filter=request_filter,
        formatter=formatter
    )
    server.run()
