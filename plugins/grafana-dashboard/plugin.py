"""Grafana Dashboard Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Grafana Dashboard"
    description = "Pre-built Grafana dashboard for Dispatcharr metrics"

    def start(self):
        logger.info("Grafana Dashboard started")

    def stop(self):
        logger.info("Grafana Dashboard stopped")
