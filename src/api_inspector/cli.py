"""
CLI entry point for API Inspector.
"""

import click
from rich.console import Console

from .proxy import start_proxy
from .filters import RequestFilter
from .formatter import OutputFormatter

console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """API Inspector - Network request inspection tool based on mitmproxy."""
    if version:
        from . import __version__
        console.print(f"api-inspector version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        # Default: start proxy with default settings
        ctx.invoke(start)


@main.command()
@click.option('--port', '-p', default=8080, help='Proxy server port (default: 8080)')
@click.option('--host', '-h', default='127.0.0.1', help='Proxy server host (default: 127.0.0.1)')
@click.option('--filter', '-f', 'url_filter', multiple=True, help='URL pattern filter (supports wildcards)')
@click.option('--method', '-m', multiple=True, help='HTTP method filter (GET, POST, PUT, DELETE, etc.)')
@click.option('--status-code', '-s', multiple=True, help='Status code filter (200, 404, 500, etc.)')
@click.option('--content-type', '-c', multiple=True, help='Content-Type filter (json, html, xml, etc.)')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--verbose', '-V', is_flag=True, help='Show detailed request/response content')
@click.option('--no-color', is_flag=True, help='Disable colored output')
def start(
    port: int,
    host: str,
    url_filter: tuple,
    method: tuple,
    status_code: tuple,
    content_type: tuple,
    json_output: bool,
    verbose: bool,
    no_color: bool
) -> None:
    """Start the proxy server and begin capturing requests.

    Examples:

        \b
        # Start with default settings (port 8080)
        api-inspector start

        \b
        # Specify a custom port
        api-inspector start --port 8888

        \b
        # Filter by domain pattern
        api-inspector start --filter "api.example.com"

        \b
        # Filter by HTTP method
        api-inspector start --method POST --method PUT

        \b
        # Filter by status code
        api-inspector start --status-code 200 --status-code 201

        \b
        # JSON output for logging
        api-inspector start --json

        \b
        # Verbose mode with full request/response bodies
        api-inspector start --verbose
    """
    # Create filter configuration
    request_filter = RequestFilter(
        url_patterns=list(url_filter) if url_filter else None,
        methods=[m.upper() for m in method] if method else None,
        status_codes=[int(s) for s in status_code] if status_code else None,
        content_types=list(content_type) if content_type else None,
    )

    # Create output formatter
    formatter = OutputFormatter(
        json_output=json_output,
        verbose=verbose,
        no_color=no_color
    )

    # Display startup banner
    if not json_output:
        formatter.print_banner(host, port)

    # Start the proxy
    try:
        start_proxy(
            host=host,
            port=port,
            request_filter=request_filter,
            formatter=formatter
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Proxy stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


@main.command()
def certs() -> None:
    """Show certificate information and installation instructions.

    HTTPS interception requires the mitmproxy CA certificate to be installed
    in your system's trust store.
    """
    import os
    from pathlib import Path

    console.print("[bold]Certificate Information[/bold]\n")

    # Default mitmproxy certificate location
    cert_dir = Path.home() / ".mitmproxy"
    ca_cert = cert_dir / "mitmproxy-ca-cert.pem"

    console.print(f"Certificate directory: [cyan]{cert_dir}[/cyan]")
    console.print(f"CA certificate: [cyan]{ca_cert}[/cyan]\n")

    if ca_cert.exists():
        console.print("[green]Certificate file exists[/green]\n")
    else:
        console.print("[yellow]Certificate not found. It will be generated on first run.[/yellow]\n")

    console.print("[bold]Installation Instructions:[/bold]\n")
    console.print("[bold]Windows:[/bold]")
    console.print("  1. Run: certutil -addstore root ~/.mitmproxy/mitmproxy-ca-cert.pem")
    console.print("  2. Or double-click the .pem file and install to 'Trusted Root Certification Authorities'\n")

    console.print("[bold]macOS:[/bold]")
    console.print("  1. Open ~/.mitmproxy/mitmproxy-ca-cert.pem in Keychain Access")
    console.print("  2. Set trust to 'Always Trust' for the certificate\n")

    console.print("[bold]Linux (Ubuntu/Debian):[/bold]")
    console.print("  1. sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt")
    console.print("  2. sudo update-ca-certificates\n")

    console.print("[bold]Configure System Proxy:[/bold]")
    console.print(f"  HTTP Proxy: 127.0.0.1:8080")
    console.print(f"  HTTPS Proxy: 127.0.0.1:8080\n")


if __name__ == '__main__':
    main()
