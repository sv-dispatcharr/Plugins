"""EPG Sync Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "EPG Sync"
    description = "Synchronizes EPG data from multiple sources"

    def start(self):
        logger.info("EPG Sync started")

    def stop(self):
        logger.info("EPG Sync stopped")
