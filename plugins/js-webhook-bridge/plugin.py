"""
JS Webhook Bridge — Dispatcharr plugin

Forwards Dispatcharr channel events to an external webhook by invoking a
bundled Node.js script (webhook_handler.js) via subprocess.  Tests CodeQL
detection of co-packaged JavaScript alongside Python.
"""

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
HANDLER_SCRIPT = os.path.join(PLUGIN_DIR, "webhook_handler.js")


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="js-webhook-bridge")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {
            "key": "webhook_url",
            "label": "Webhook URL",
            "type": "text",
            "default": "",
            "description": "HTTP(S) endpoint to POST events to.",
        },
        {
            "key": "secret",
            "label": "Signing Secret",
            "type": "password",
            "default": "",
            "description": "Optional HMAC secret added to the X-Hub-Signature header.",
        },
    ]


def get_actions():
    return [
        {
            "key": "test_webhook",
            "label": "Send Test Ping",
            "description": "POST a test payload to the configured webhook URL.",
        }
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "test_webhook":
        url = settings.get("webhook_url", "").strip()
        if not url:
            return {"success": False, "message": "No webhook URL configured."}
        return _invoke_handler({"event": "ping", "url": url, "secret": settings.get("secret", "")})
    return {"success": False, "message": f"Unknown action: {action_key}"}


def _invoke_handler(payload):
    try:
        result = subprocess.run(
            ["node", HANDLER_SCRIPT],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"success": True, "message": result.stdout.strip() or "OK"}
        return {"success": False, "message": result.stderr.strip() or "Handler exited non-zero"}
    except FileNotFoundError:
        return {"success": False, "message": "Node.js is not available on this system."}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Webhook handler timed out."}
    except Exception as e:
        logger.exception("js-webhook-bridge: unexpected error invoking handler")
        return {"success": False, "message": str(e)}
