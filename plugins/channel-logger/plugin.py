"""Channel Logger Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Channel Logger"
    description = "Logs channel activity and stream changes"

    def start(self):
        logger.info("Channel Logger started")

    def stop(self):
        logger.info("Channel Logger stopped")
