"""Channel Sorter Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Channel Sorter"
    description = "Sorts and organizes channels by custom rules"

    def start(self):
        logger.info("Channel Sorter started")

    def stop(self):
        logger.info("Channel Sorter stopped")
