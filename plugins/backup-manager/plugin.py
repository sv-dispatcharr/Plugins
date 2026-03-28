"""Backup Manager Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Backup Manager"
    description = "Automated backup and restore of configuration"

    def start(self):
        logger.info("Backup Manager started")

    def stop(self):
        logger.info("Backup Manager stopped")
