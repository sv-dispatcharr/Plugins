"""Stream Health Monitor Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Stream Health Monitor"
    description = "Monitors stream health and sends alerts"

    def start(self):
        logger.info("Stream Health Monitor started")

    def stop(self):
        logger.info("Stream Health Monitor stopped")
