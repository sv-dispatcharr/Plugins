import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Confirm Action Demo"
    version = "1.0.0"
    description = "Demonstrates the confirm modal on a destructive-looking action."
    author = "irinakorb"

    actions = [
        {
            "id": "safe_run",
            "label": "Safe Run",
            "description": "Runs without a confirmation prompt.",
            "button_label": "Run",
            "button_variant": "filled",
            "button_color": "green",
        },
        {
            "id": "risky_run",
            "label": "Risky Run",
            "description": "Requires confirmation before running.",
            "button_label": "Run (Confirm)",
            "button_variant": "filled",
            "button_color": "red",
            "confirm": {
                "required": True,
                "title": "Are you sure?",
                "message": "This action is just a demo, but pretend it's destructive.",
            },
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "safe_run":
            log.info("confirm-action-demo: safe_run executed (no confirmation required)")
            return {"status": "ok", "action": "safe_run"}
        if action == "risky_run":
            log.info("confirm-action-demo: risky_run executed after user confirmation")
            return {"status": "ok", "action": "risky_run"}
        return {"status": "error", "message": f"Unknown action: {action}"}
