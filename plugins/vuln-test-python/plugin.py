"""
Vuln Test Python — Dispatcharr plugin

!! TEST FIXTURE ONLY — intentionally vulnerable code !!

Contains multiple high/critical CodeQL violations to verify that the
validate-plugin workflow correctly detects, blocks, and reports them.

Violations present:
  - py/sql-injection       (CVSS 9.8) — unsanitised user input in raw SQL
  - py/command-injection   (CVSS 9.8) — user input passed to shell via subprocess
  - py/code-injection      (CVSS 9.8) — eval() on user-controlled data
  - py/path-injection      (CVSS 7.5) — unsanitised path used in open()
  - py/unsafe-deserialization (CVSS 9.8) — pickle.loads on user-supplied bytes
"""

import logging
import os
import pickle
import subprocess

logger = logging.getLogger(__name__)


def get_settings_fields():
    return [
        {"key": "search_term",  "label": "Search Term",   "type": "text",   "default": ""},
        {"key": "export_path",  "label": "Export Path",   "type": "text",   "default": "/tmp/export.txt"},
        {"key": "shell_cmd",    "label": "Shell Command", "type": "text",   "default": "echo hello"},
        {"key": "eval_expr",    "label": "Expression",    "type": "text",   "default": "1+1"},
    ]


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="vuln-test-python")
        return cfg.settings or {}
    except Exception:
        return {}


def get_actions():
    return [
        {"key": "search_channels",  "label": "Search Channels"},
        {"key": "export_results",   "label": "Export Results"},
        {"key": "run_shell",        "label": "Run Shell Command"},
        {"key": "evaluate",         "label": "Evaluate Expression"},
        {"key": "load_state",       "label": "Load Saved State"},
    ]


def run_action(action_key, params=None):
    settings = _get_settings()

    if action_key == "search_channels":
        # py/sql-injection: user-controlled string interpolated directly into SQL.
        term = settings.get("search_term", "")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM channels_channel WHERE name LIKE '%" + term + "%'"
            )
            rows = cursor.fetchall()
        return {"success": True, "message": f"Found {len(rows)} channel(s)."}

    if action_key == "export_results":
        # py/path-injection: user-supplied path passed directly to open().
        path = settings.get("export_path", "/tmp/export.txt")
        with open(path, "w") as fh:
            fh.write("export data\n")
        return {"success": True, "message": f"Exported to {path}"}

    if action_key == "run_shell":
        # py/command-injection: user-supplied string executed as a shell command.
        cmd = settings.get("shell_cmd", "echo hello")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {"success": True, "message": result.stdout.strip()}

    if action_key == "evaluate":
        # py/code-injection: eval() on user-controlled input.
        expr = settings.get("eval_expr", "1+1")
        value = eval(expr)
        return {"success": True, "message": str(value)}

    if action_key == "load_state":
        # py/unsafe-deserialization: pickle.loads on bytes read from a user-specified path.
        path = settings.get("export_path", "/tmp/state.pkl")
        with open(path, "rb") as fh:
            data = fh.read()
        obj = pickle.loads(data)
        return {"success": True, "message": str(obj)}

    return {"success": False, "message": f"Unknown action: {action_key}"}
