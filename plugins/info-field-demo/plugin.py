import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "Info Field Demo"
    version = "1.0.0"
    description = "Demonstrates the info (display-only) field type for headings and notes."
    author = "maddoxwren"

    fields = [
        {
            "id": "section_header",
            "label": "Connection Settings",
            "type": "info",
            "description": "Configure the connection parameters below.",
        },
        {"id": "host", "label": "Host", "type": "string", "default": "localhost",
         "help_text": "The remote host to connect to."},
        {"id": "port", "label": "Port", "type": "number", "default": 8080},
        {
            "id": "note",
            "label": "",
            "type": "info",
            "description": "Changes are saved automatically when you click Save Settings.",
        },
    ]

    actions = [
        {
            "id": "log_config",
            "label": "Log Config",
            "description": "Logs the current host and port settings.",
            "button_label": "Log Config",
            "button_variant": "subtle",
            "button_color": "blue",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "log_config":
            settings = context.get("settings", {})
            host = settings.get("host", "localhost")
            port = settings.get("port", 8080)
            log.info("info-field-demo: host=%s port=%s", host, port)
            return {"status": "ok", "host": host, "port": port}
        return {"status": "error", "message": f"Unknown action: {action}"}
