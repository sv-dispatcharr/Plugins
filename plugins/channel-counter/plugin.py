import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Channel Counter"
    version = "1.0.0"
    description = "Counts channels in the database and logs the total."
    author = "prixdevs"

    actions = [
        {
            "id": "count_channels",
            "label": "Count Channels",
            "description": "Queries the DB for the total channel count and logs it.",
            "button_label": "Count",
            "button_variant": "filled",
            "button_color": "teal",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "count_channels":
            try:
                from apps.channels.models import Channel
                count = Channel.objects.count()
                log.info("channel-counter: total channels in DB = %d", count)
                return {"status": "ok", "count": count}
            except Exception as exc:
                log.error("channel-counter: failed to count channels: %s", exc)
                return {"status": "error", "message": str(exc)}
        return {"status": "error", "message": f"Unknown action: {action}"}
