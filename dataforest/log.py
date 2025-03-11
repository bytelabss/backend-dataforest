import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from werkzeug import serving
from rich.logging import RichHandler


def init_log(config):
    level = logging.DEBUG if config.APP_DEBUG else logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)

    if config.APP_ENV == "development":
        # Development logging with Rich
        handler = RichHandler(
            rich_tracebacks=True, tracebacks_show_locals=True, markup=True
        )
        handler.setLevel(level)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Patch Werkzeug to use rich markup instead of ANSI codes
        def _werkzeug_ansi_style_patched_to_use_rich_markup(
            value: str, *styles: str
        ) -> str:
            if not serving._log_add_style:
                return value
            return f"[{' '.join(styles)}]{value}[/]"

        serving._ansi_style = _werkzeug_ansi_style_patched_to_use_rich_markup

        # SQLAlchemy
        if config.SQLALCHEMY_ECHO:
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

        logging.info("Rich logging configured for development.")
    elif config.APP_ENV == "production":
        # Production logging
        log_file_path = Path(config.PROJECT_DIR) / "logs" / f"{config.APP_MODULE}.log"
        os.makedirs(log_file_path.parent, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logging.info("Logging configured for production.")
