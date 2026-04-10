"""
Vuln Test JavaScript — Dispatcharr plugin

!! TEST FIXTURE ONLY — intentionally vulnerable code !!

Invokes the bundled handler.js which contains high/critical CodeQL violations
to verify that the validate-plugin workflow detects JavaScript security issues.
"""

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
HANDLER = os.path.join(PLUGIN_DIR, "handler.js")


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="vuln-test-javascript")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {"key": "query",      "label": "Search Query",  "type": "text", "default": ""},
        {"key": "file_path",  "label": "File Path",     "type": "text", "default": "/tmp/data.txt"},
        {"key": "shell_cmd",  "label": "Shell Command", "type": "text", "default": "echo hello"},
        {"key": "expression", "label": "JS Expression", "type": "text", "default": "1+1"},
    ]


def get_actions():
    return [
        {"key": "run", "label": "Run JS Handler"},
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "run":
        try:
            result = subprocess.run(
                ["node", HANDLER],
                input=json.dumps(settings),
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            return {"success": False, "message": result.stderr.strip()}
        except FileNotFoundError:
            return {"success": False, "message": "Node.js not found."}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Handler timed out."}
    return {"success": False, "message": f"Unknown action: {action_key}"}
