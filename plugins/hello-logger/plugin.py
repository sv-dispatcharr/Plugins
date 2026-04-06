import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Hello Logger"
    version = "1.0.0"
    description = "A minimal hello-world plugin that logs a greeting message."
    author = "nachtfalter"

    actions = [
        {
            "id": "say_hello",
            "label": "Say Hello",
            "description": "Logs a hello-world message at INFO level.",
            "button_label": "Say Hello",
            "button_variant": "filled",
            "button_color": "blue",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "say_hello":
            log.info("Hello from Hello Logger plugin!")
            return {"status": "ok", "message": "Hello, world!"}
        return {"status": "error", "message": f"Unknown action: {action}"}
