import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Retired Internal Tool"
    version = "2.0.0"
    description = (
        "A retired internal plugin that is both deprecated and unlisted. "
        "Its per-plugin manifest still exists but it does not appear in the root manifest."
    )
    author = "pelikandev"

    actions = [
        {
            "id": "run",
            "label": "Run",
            "description": "Logs a retirement notice at WARNING and INFO level.",
            "button_label": "Run",
            "button_variant": "outline",
            "button_color": "gray",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "run":
            log.warning(
                "retired-internal-tool: this plugin is deprecated AND unlisted — it should not appear in the plugin hub."
            )
            log.info("retired-internal-tool: hello from a retired, unlisted plugin")
            return {"status": "ok", "deprecated": True, "unlisted": True}
        return {"status": "error", "message": f"Unknown action: {action}"}
