import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "M3U Lister"
    version = "1.0.0"
    description = "Logs the names of all M3U accounts configured in Dispatcharr."
    author = "tobiasfendt"

    actions = [
        {
            "id": "list_m3u",
            "label": "List M3U Accounts",
            "description": "Logs all M3U account names at INFO level.",
            "button_label": "List",
            "button_variant": "outline",
            "button_color": "cyan",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "list_m3u":
            try:
                from apps.m3u.models import M3UAccount
                names = list(M3UAccount.objects.values_list("name", flat=True))
                log.info("m3u-lister: M3U accounts = %s", names)
                return {"status": "ok", "accounts": names, "count": len(names)}
            except Exception as exc:
                log.error("m3u-lister: error listing M3U accounts: %s", exc)
                return {"status": "error", "message": str(exc)}
        return {"status": "error", "message": f"Unknown action: {action}"}
