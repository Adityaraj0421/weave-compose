"""weave serve command — starts the Weave local FastAPI server."""

import typer


def serve(
    port: int = typer.Option(
        7842,
        "--port",
        "-p",
        help="Port to listen on (default: 7842)",
    ),
) -> None:
    """Start the Weave local FastAPI server on localhost.

    Launches uvicorn at ``http://localhost:<port>`` and prints the URL before
    blocking. Press Ctrl+C to stop. Requires the server optional extra::

        pip install weave-compose[server]

    Args:
        port: TCP port to bind to. Defaults to 7842.
    """
    try:
        import uvicorn
    except ImportError:
        typer.echo(
            "Error: uvicorn is not installed. Run: pip install weave-compose[server]",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Starting Weave server at http://localhost:{port}")
    typer.echo("Press Ctrl+C to stop.")
    uvicorn.run("weave.server.app:app", host="127.0.0.1", port=port, reload=False)
