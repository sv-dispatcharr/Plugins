import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Legacy Notifier"
    version = "1.2.0"
    description = "An older notification plugin superseded by a newer approach. Kept for reference only."
    author = "hartleydev"

    actions = [
        {
            "id": "notify",
            "label": "Notify",
            "description": "Logs a deprecation warning and a hello-world message.",
            "button_label": "Notify",
            "button_variant": "outline",
            "button_color": "gray",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "notify":
            log.warning(
                "legacy-notifier: this plugin is deprecated and may be removed in a future release."
            )
            log.info("legacy-notifier: hello from the deprecated notifier")
            return {"status": "ok", "deprecated": True}
        return {"status": "error", "message": f"Unknown action: {action}"}
