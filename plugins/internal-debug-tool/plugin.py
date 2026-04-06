import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Internal Debug Tool"
    version = "1.0.0"
    description = (
        "An internal diagnostics plugin not intended for general distribution. "
        "Unlisted from the root manifest."
    )
    author = "nnvoss"

    actions = [
        {
            "id": "debug",
            "label": "Debug",
            "description": "Logs internal debug info at INFO level.",
            "button_label": "Debug",
            "button_variant": "subtle",
            "button_color": "gray",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "debug":
            log.info(
                "internal-debug-tool: hello from the unlisted internal debug plugin"
            )
            return {"status": "ok", "unlisted": True}
        return {"status": "error", "message": f"Unknown action: {action}"}
