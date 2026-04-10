"""
Shell Backup Helper — Dispatcharr plugin

Invokes a bundled shell script (backup.sh) to archive Dispatcharr data to the
path configured in settings.  Tests the CodeQL workflow's unscanned-shell notice:
plugin.py is scanned by CodeQL, but backup.sh is not (shell is not a supported
CodeQL language) and should appear in the informational unscanned-langs callout.
"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_SCRIPT = os.path.join(PLUGIN_DIR, "backup.sh")


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="shell-backup-helper")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {
            "key": "backup_path",
            "label": "Backup Destination",
            "type": "text",
            "default": "/backups/dispatcharr",
            "description": "Absolute path where the backup archive will be written.",
        },
        {
            "key": "retain_days",
            "label": "Retain (days)",
            "type": "number",
            "default": 7,
            "description": "Delete archives older than this many days.",
        },
    ]


def get_actions():
    return [
        {
            "key": "run_backup",
            "label": "Run Backup Now",
            "description": "Execute the backup script immediately.",
        }
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "run_backup":
        backup_path = settings.get("backup_path", "/backups/dispatcharr").strip()
        retain_days = str(settings.get("retain_days", 7))
        try:
            result = subprocess.run(
                ["bash", BACKUP_SCRIPT, backup_path, retain_days],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip() or "Backup completed."}
            return {"success": False, "message": result.stderr.strip() or "Backup script exited non-zero."}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Backup timed out after 120 seconds."}
        except Exception as e:
            logger.exception("shell-backup-helper: unexpected error running backup")
            return {"success": False, "message": str(e)}
    return {"success": False, "message": f"Unknown action: {action_key}"}
