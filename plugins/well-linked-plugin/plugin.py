import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Well Linked Plugin"
    version = "1.0.0"
    description = (
        "A demo plugin with a full set of metadata links — "
        "repo URL, Discord thread, and license."
    )
    author = "jasperveld"

    actions = [
        {
            "id": "run",
            "label": "Run",
            "description": "Logs a hello message.",
            "button_label": "Run",
            "button_variant": "filled",
            "button_color": "blue",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "run":
            log.info("well-linked-plugin: hello from a fully-linked plugin")
            return {"status": "ok"}
        return {"status": "error", "message": f"Unknown action: {action}"}
