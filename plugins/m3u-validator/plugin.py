"""M3U Validator Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "M3U Validator"
    description = "Validates M3U playlists and reports issues"

    def start(self):
        logger.info("M3U Validator started")

    def stop(self):
        logger.info("M3U Validator stopped")
