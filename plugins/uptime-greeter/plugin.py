import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Plugin:
    name = "Uptime Greeter"
    version = "1.0.0"
    description = "Logs a configurable greeting with the current server timestamp."
    author = "wrenwick"

    fields = [
        {
            "id": "greeting",
            "label": "Greeting",
            "type": "string",
            "default": "Dispatcharr is alive",
            "help_text": "The message to log when the action is triggered.",
        },
    ]

    actions = [
        {
            "id": "greet",
            "label": "Greet",
            "description": "Logs the greeting with the current timestamp.",
            "button_label": "Greet",
            "button_variant": "filled",
            "button_color": "green",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "greet":
            settings = context.get("settings", {})
            greeting = settings.get("greeting", "Dispatcharr is alive")
            now = datetime.now(timezone.utc).isoformat()
            log.info("uptime-greeter: %s [%s]", greeting, now)
            return {"status": "ok", "message": greeting, "timestamp": now}
        return {"status": "error", "message": f"Unknown action: {action}"}
