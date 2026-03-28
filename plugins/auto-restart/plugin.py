"""Auto Restart Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Auto Restart"
    description = "Automatically restarts failed streams"

    def start(self):
        logger.info("Auto Restart started")

    def stop(self):
        logger.info("Auto Restart stopped")
