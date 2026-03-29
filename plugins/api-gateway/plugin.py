"""API Gateway Plugin - Dummy for manifest testing TEST"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "API Gateway"
    description = "REST API gateway for third-party integrations"

    def start(self):
        logger.info("API Gateway started")

    def stop(self):
        logger.info("API Gateway stopped")
