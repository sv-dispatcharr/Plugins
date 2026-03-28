"""Discord Notifier Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Discord Notifier"
    description = "Sends Discord webhook notifications for stream events"

    def start(self):
        logger.info("Discord Notifier started")

    def stop(self):
        logger.info("Discord Notifier stopped")
