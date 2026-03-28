"""Bandwidth Limiter Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Bandwidth Limiter"
    description = "Limits total bandwidth usage per profile"

    def start(self):
        logger.info("Bandwidth Limiter started")

    def stop(self):
        logger.info("Bandwidth Limiter stopped")
