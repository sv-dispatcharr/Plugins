import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Version Gated Plugin"
    version = "1.0.0"
    description = (
        "Only compatible with a specific Dispatcharr version range. "
        "Used to test version gating in the plugin hub."
    )
    author = "cosmicreed"

    actions = [
        {
            "id": "run",
            "label": "Run",
            "description": "Logs a hello message confirming the version gate was passed.",
            "button_label": "Run",
            "button_variant": "filled",
            "button_color": "lime",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "run":
            log.info(
                "version-gated-plugin: hello — version gate passed (requires v0.20.0–v0.21.99)"
            )
            return {"status": "ok"}
        return {"status": "error", "message": f"Unknown action: {action}"}
