"""Telegram Bot Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Telegram Bot"
    description = "Telegram bot for remote Dispatcharr control"

    def start(self):
        logger.info("Telegram Bot started")

    def stop(self):
        logger.info("Telegram Bot stopped")
