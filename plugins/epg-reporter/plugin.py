import logging

logger = logging.getLogger(__name__)


class Plugin:
    name = "EPG Reporter"
    version = "1.0.0"
    description = "Logs the number of EPG sources configured in Dispatcharr."
    author = "solarflux42"

    actions = [
        {
            "id": "report",
            "label": "Report EPG Sources",
            "description": "Logs the total count of EPG sources at INFO level.",
            "button_label": "Report",
            "button_variant": "filled",
            "button_color": "orange",
        },
    ]

    def run(self, action: str, params: dict, context: dict):
        log = context.get("logger", logger)
        if action == "report":
            try:
                from apps.epg.models import EPGSource
                count = EPGSource.objects.count()
                log.info("epg-reporter: total EPG sources = %d", count)
                return {"status": "ok", "epg_source_count": count}
            except Exception as exc:
                log.error("epg-reporter: error querying EPG sources: %s", exc)
                return {"status": "error", "message": str(exc)}
        return {"status": "error", "message": f"Unknown action: {action}"}
