"""
Mixed Lang Bundle — Dispatcharr plugin

Bundles Python + TypeScript (scanned by CodeQL) alongside shell and Lua
(not scanned by CodeQL).  The intent is to exercise the workflow path where:
  - Python and javascript (TypeScript) appear in the CodeQL scanned-languages list
  - shell and lua appear in the unscanned-langs informational callout

The plugin itself is a simple channel-annotation tool: a TypeScript helper
normalises display names, a shell script writes a nightly report file, and a
Lua snippet evaluates custom tag rules.
"""

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="mixed-lang-bundle")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {
            "key": "report_dir",
            "label": "Report Output Directory",
            "type": "text",
            "default": "/tmp/dispatcharr-reports",
        },
        {
            "key": "ts_node_path",
            "label": "ts-node Binary",
            "type": "text",
            "default": "ts-node",
            "description": "Path to ts-node (TypeScript runner).",
        },
    ]


def get_actions():
    return [
        {
            "key": "normalise_names",
            "label": "Normalise Channel Names",
            "description": "Run the TypeScript name normaliser over the channel list.",
        },
        {
            "key": "write_report",
            "label": "Write Nightly Report",
            "description": "Execute the shell report writer.",
        },
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "normalise_names":
        return _run_ts_normaliser(settings)
    if action_key == "write_report":
        return _run_shell_report(settings)
    return {"success": False, "message": f"Unknown action: {action_key}"}


def _run_ts_normaliser(settings):
    try:
        from apps.channels.models import Channel
        names = list(Channel.objects.values_list("name", flat=True)[:200])
    except Exception as e:
        return {"success": False, "message": f"Could not load channels: {e}"}

    ts_node = settings.get("ts_node_path", "ts-node").strip() or "ts-node"
    script = os.path.join(PLUGIN_DIR, "normalise.ts")
    try:
        result = subprocess.run(
            [ts_node, script],
            input=json.dumps(names),
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            return {"success": True, "message": result.stdout.strip()}
        return {"success": False, "message": result.stderr.strip()}
    except FileNotFoundError:
        return {"success": False, "message": f"ts-node not found: {ts_node}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "TypeScript normaliser timed out."}


def _run_shell_report(settings):
    report_dir = settings.get("report_dir", "/tmp/dispatcharr-reports").strip()
    script = os.path.join(PLUGIN_DIR, "write_report.sh")
    try:
        result = subprocess.run(
            ["bash", script, report_dir],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return {"success": True, "message": result.stdout.strip()}
        return {"success": False, "message": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Shell report writer timed out."}
    except Exception as e:
        logger.exception("mixed-lang-bundle: unexpected error in shell report")
        return {"success": False, "message": str(e)}
