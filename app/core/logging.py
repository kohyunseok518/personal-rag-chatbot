import logging


LOG_FORMAT = (
    "%(asctime)s "
    "%(levelname)s "
    "%(name)s "
    "%(message)s"
)


def configure_logging(log_level: str) -> None:
    resolved_level = getattr(
        logging,
        log_level.upper(),
        logging.INFO,
    )

    logging.basicConfig(
        level=resolved_level,
        format=LOG_FORMAT,
    )

    logging.getLogger().setLevel(resolved_level)