"""Webhook Relay Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Webhook Relay"
    description = "Forwards Dispatcharr events to HTTP endpoints"

    def start(self):
        logger.info("Webhook Relay started")

    def stop(self):
        logger.info("Webhook Relay stopped")
