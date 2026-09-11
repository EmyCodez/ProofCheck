import logging


def configure_logging() -> None:
    """Configure safe application logging for ProofCheck."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
