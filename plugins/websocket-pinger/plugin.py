import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "WebSocket Pinger"
    version = "1.0.0"
    description = "Sends a test WebSocket update to the UI and logs confirmation."
    author = "radarlabs"

    actions = [
        {
            "id": "ping",
            "label": "Ping UI",
            "description": "Sends a test WebSocket message and logs the result.",
            "button_label": "Ping",
            "button_variant": "filled",
            "button_color": "indigo",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "ping":
            try:
                from core.utils import send_websocket_update
                send_websocket_update(
                    "updates",
                    "update",
                    {"type": "plugin", "plugin": "websocket-pinger", "message": "ping"},
                )
                log.info("websocket-pinger: WebSocket ping sent successfully")
                return {"status": "ok", "message": "ping sent"}
            except Exception as exc:
                log.error("websocket-pinger: failed to send WebSocket ping: %s", exc)
                return {"status": "error", "message": str(exc)}
        return {"status": "error", "message": f"Unknown action: {action}"}
