import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Password Field Demo"
    version = "1.0.0"
    description = "Demonstrates the password input_type on a string field."
    author = "quentinash"

    fields = [
        {
            "id": "api_key",
            "label": "API Key",
            "type": "string",
            "input_type": "password",
            "default": "",
            "help_text": "Stored masked. Logged length only, never the value.",
        },
    ]

    actions = [
        {
            "id": "check_key",
            "label": "Check Key",
            "description": "Logs whether an API key has been configured (not the value).",
            "button_label": "Check Key",
            "button_variant": "outline",
            "button_color": "yellow",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "check_key":
            settings = context.get("settings", {})
            key = settings.get("api_key", "")
            if key:
                log.info("password-field-demo: API key is set (length=%d)", len(key))
                return {"status": "ok", "key_set": True}
            log.info("password-field-demo: no API key configured")
            return {"status": "ok", "key_set": False}
        return {"status": "error", "message": f"Unknown action: {action}"}
