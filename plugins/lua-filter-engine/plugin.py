"""
Lua Filter Engine — Dispatcharr plugin

Passes the channel list through a bundled Lua script (channel_rules.lua) via
the lupa or lunatic bridge, allowing power users to write filter/rank logic in
Lua without modifying the plugin itself.

Tests the CodeQL workflow's unscanned-language notice: plugin.py is scanned,
but channel_rules.lua is not (Lua has no CodeQL support) and should appear in
the informational unscanned-langs callout.
"""

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
LUA_SCRIPT = os.path.join(PLUGIN_DIR, "channel_rules.lua")


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="lua-filter-engine")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {
            "key": "lua_binary",
            "label": "Lua Binary Path",
            "type": "text",
            "default": "lua",
            "description": "Path to the lua5.x interpreter on the host.",
        },
        {
            "key": "min_score",
            "label": "Minimum Score",
            "type": "number",
            "default": 0,
            "description": "Streams with a score below this threshold are excluded.",
        },
    ]


def get_actions():
    return [
        {
            "key": "preview_filter",
            "label": "Preview Filter Output",
            "description": "Run the Lua filter on the current channel list and return the result.",
        }
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "preview_filter":
        return _run_lua_filter(settings)
    return {"success": False, "message": f"Unknown action: {action_key}"}


def _run_lua_filter(settings):
    try:
        from apps.channels.models import Channel
        channels = list(Channel.objects.values("uuid", "name", "number"))
    except Exception as e:
        return {"success": False, "message": f"Could not load channels: {e}"}

    lua_bin = settings.get("lua_binary", "lua").strip() or "lua"
    min_score = settings.get("min_score", 0)
    payload = json.dumps({"channels": channels, "min_score": min_score})

    try:
        result = subprocess.run(
            [lua_bin, LUA_SCRIPT],
            input=payload,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return {"success": True, "message": result.stdout.strip()}
        return {"success": False, "message": result.stderr.strip() or "Lua script exited non-zero."}
    except FileNotFoundError:
        return {"success": False, "message": f"Lua interpreter not found: {lua_bin}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Lua filter timed out after 15 seconds."}
    except Exception as e:
        logger.exception("lua-filter-engine: unexpected error")
        return {"success": False, "message": str(e)}
