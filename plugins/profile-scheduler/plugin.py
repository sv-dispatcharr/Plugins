"""Profile Scheduler Plugin - Dummy for manifest testing"""
import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Profile Scheduler"
    description = "Schedules automatic profile switching"

    def start(self):
        logger.info("Profile Scheduler started")

    def stop(self):
        logger.info("Profile Scheduler stopped")
