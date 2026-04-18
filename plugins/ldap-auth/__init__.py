"""LDAP Auth - package root.

Dispatcharr discovers the plugin by importing this package and looking for
the ``Plugin`` class.  LDAP connection logic lives in ldap_backend.py;
this file only contains the plugin API and the authentication hooks.
"""

import logging

from .config import PLUGIN_CONFIG, PLUGIN_FIELDS, PLUGIN_DB_KEY

logger = logging.getLogger(__name__)


def _load_settings() -> dict:
    """Read current plugin settings from the database, merged with defaults."""
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key=PLUGIN_DB_KEY)
        if not cfg.enabled:
            return {}
        settings = cfg.settings or {}
        # Merge defaults from field definitions
        for field in PLUGIN_FIELDS:
            fid = field.get("id", "")
            if fid and fid not in settings and "default" in field:
                settings[fid] = field["default"]
        return settings
    except Exception:
        return {}


class Plugin:
    """Dispatcharr Plugin - LDAP / Active Directory authentication."""

    name        = PLUGIN_CONFIG["name"]
    description = PLUGIN_CONFIG["description"]
    version     = PLUGIN_CONFIG["version"]
    author      = PLUGIN_CONFIG["author"]

    fields  = PLUGIN_FIELDS
    actions = [
        {
            "id": "test_connection",
            "label": "Test Connection",
            "description": "Verify connectivity to the LDAP server",
            "button_label": "Test Connection",
            "button_variant": "filled",
            "button_color": "blue",
        },
        {
            "id": "test_login",
            "label": "Test Login",
            "description": "Authenticate a specific user against LDAP",
            "button_label": "Test Login",
            "button_variant": "filled",
            "button_color": "green",
            "fields": [
                {"id": "username", "label": "Username", "type": "string"},
                {"id": "password", "label": "Password", "type": "password"},
            ],
        },
        {
            "id": "clear_cache",
            "label": "Clear Auth Cache",
            "description": "Purge all cached LDAP authentication results",
            "button_label": "Clear Cache",
            "button_variant": "filled",
            "button_color": "orange",
        },
    ]

    # -- Plugin authentication hooks ------------------------------------------
    # These methods are called by Dispatcharr's plugin auth system.
    # authenticate_ui: called by PluginAuthBackend (Django authentication backend)
    # authenticate_xc: called by xc_get_user() for XC endpoint auth

    def authenticate_ui(self, username: str, password: str):
        """Authenticate a user for UI login via LDAP.

        Returns a Django User on success, or None to pass to the next backend.
        """
        settings = _load_settings()
        if not settings or not settings.get("enable_ui_auth", True):
            return None

        from .ldap_backend import authenticate
        return authenticate(username, password, settings)

    def authenticate_xc(self, username: str, password: str):
        """Authenticate a user for XC endpoints via LDAP.

        Returns a Django User on success, or None to pass to the next backend.
        """
        settings = _load_settings()
        if not settings or not settings.get("enable_xc_auth", False):
            return None

        from .ldap_backend import authenticate
        return authenticate(username, password, settings)

    # -- Action dispatcher ----------------------------------------------------

    def run(self, action: str, params: dict, context: dict):
        """Execute a plugin action and return a result dict."""
        settings = context.get("settings", {})

        if action == "test_connection":
            from .ldap_backend import test_connection
            return test_connection(settings)

        elif action == "test_login":
            username = params.get("username", "")
            password = params.get("password", "")
            from .ldap_backend import test_login
            return test_login(username, password, settings)

        elif action == "clear_cache":
            from .ldap_backend import clear_cache
            clear_cache()
            return {"status": "success", "message": "Auth cache cleared"}

        return {"status": "error", "message": f"Unknown action: {action}"}

    def stop(self, context: dict):
        """Called when the plugin is disabled or deleted."""
        from .ldap_backend import clear_cache
        clear_cache()
        logger.info("LDAP Auth plugin stopped, auth cache cleared")
