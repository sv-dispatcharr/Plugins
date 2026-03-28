"""Usage Stats Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Usage Stats"
    description = "Tracks detailed usage statistics"

    def start(self):
        logger.info("Usage Stats started")

    def stop(self):
        logger.info("Usage Stats stopped")
