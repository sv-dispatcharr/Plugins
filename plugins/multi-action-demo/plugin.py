import logging

logger = logging.getLogger(__name__)

_ACTIONS = {"action_one", "action_two", "action_three"}


class Plugin:
    name = "Multi Action Demo"
    version = "1.0.0"
    description = "Demonstrates multiple actions on a single plugin card."
    author = "devklara"

    actions = [
        {
            "id": "action_one",
            "label": "Action One",
            "description": "Logs 'action one triggered'.",
            "button_label": "One",
            "button_variant": "filled",
            "button_color": "blue",
        },
        {
            "id": "action_two",
            "label": "Action Two",
            "description": "Logs 'action two triggered'.",
            "button_label": "Two",
            "button_variant": "filled",
            "button_color": "red",
        },
        {
            "id": "action_three",
            "label": "Action Three",
            "description": "Logs 'action three triggered'.",
            "button_label": "Three",
            "button_variant": "outline",
            "button_color": "gray",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action in _ACTIONS:
            log.info("multi-action-demo: %s triggered", action)
            return {"status": "ok", "action": action}
        return {"status": "error", "message": f"Unknown action: {action}"}
