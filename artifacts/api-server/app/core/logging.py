import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure JSON-shaped structured logs without leaking request secrets."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stdout,
        format=(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        ),
        force=True,
    )