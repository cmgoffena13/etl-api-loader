import asyncio
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler
from typer import Option, Typer

from src.logging_conf import setup_logging
from src.processor.processor import Processor

app = Typer(help="API Loader - ETL Pipeline for APIs")
console = Console()


@app.command()
def process(
    source: Optional[str] = Option(
        None, "--source", "-s", help="API Source to process Ex. dummyjson"
    ),
    endpoint: Optional[str] = Option(
        None, "--endpoint", "-e", help="API Endpoint to process Ex. products"
    ),
) -> None:
    root_logger = structlog.get_logger("src")
    for handler in root_logger.handlers:
        if isinstance(handler, RichHandler):
            handler.console = console
            handler.show_time = False
            handler.show_path = False

    processor = Processor()
    if source and endpoint:
        console.print(
            f"[green]Processing endpoint {endpoint} from source {source}...[/green]"
        )
        asyncio.run(processor.process_endpoint(source, endpoint))
    elif source:
        console.print(f"[green]Processing API {source}...[/green]")
        asyncio.run(processor.process_api(source))
    else:
        console.print("[green]Processing all APIs...[/green]")
        processor.process()


def main() -> None:
    setup_logging()
    app()


if __name__ == "__main__":
    main()
