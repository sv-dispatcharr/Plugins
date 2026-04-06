import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Settings Tester"
    version = "1.0.0"
    description = "Exercises every field type and logs the current settings values."
    author = "kelvinmoss"

    fields = [
        {"id": "text_field", "label": "Text Field", "type": "string", "default": "hello"},
        {"id": "number_field", "label": "Number Field", "type": "number", "default": 42},
        {"id": "bool_field", "label": "Boolean Field", "type": "boolean", "default": True},
        {
            "id": "select_field",
            "label": "Select Field",
            "type": "select",
            "default": "a",
            "options": [
                {"value": "a", "label": "Option A"},
                {"value": "b", "label": "Option B"},
                {"value": "c", "label": "Option C"},
            ],
        },
        {"id": "textarea_field", "label": "Textarea Field", "type": "text", "default": "multi\nline"},
    ]

    actions = [
        {
            "id": "log_settings",
            "label": "Log Settings",
            "description": "Logs all current settings values at INFO level.",
            "button_label": "Log Settings",
            "button_variant": "outline",
            "button_color": "violet",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "log_settings":
            settings = context.get("settings", {})
            log.info("settings-tester: current settings = %s", settings)
            return {"status": "ok", "settings": settings}
        return {"status": "error", "message": f"Unknown action: {action}"}
