import logging
from enum import Enum

from typer import Typer

from arine.tools.greenhouse.cli.commands.recruiting.app import recruiting_app
from arine.tools.greenhouse.cli.commands.session.app import session_app

app = Typer()
app.add_typer(recruiting_app)
app.add_typer(session_app)


class LogLevel(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = "notset"


def configure_logging(level: LogLevel):
    """Configure logging based on the chosen log level."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")


@app.callback()
def app_callback(log_level: LogLevel = LogLevel.INFO):
    configure_logging(log_level)
    logging.info(f"Logging set to {log_level} level.")


def entrypoint():
    app()


if __name__ == "__main__":
    entrypoint()
