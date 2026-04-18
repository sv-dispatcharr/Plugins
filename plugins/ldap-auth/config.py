"""Plugin configuration, constants, and field definitions.

Single source of truth for:
  - PLUGIN_CONFIG: loaded from plugin.json
  - PLUGIN_FIELDS: the settings schema for the Dispatcharr UI
  - Default values for LDAP connection parameters
"""

import json
import os


# ── Hard-coded defaults ─────────────────────────────────────────────────────
DEFAULT_LDAP_PORT: int = 389
DEFAULT_LDAPS_PORT: int = 636
DEFAULT_SEARCH_SCOPE: str = "subtree"
DEFAULT_USER_LEVEL: int = 0   # Streamer
DEFAULT_CACHE_TTL: int = 300  # seconds (5 minutes)

PLUGIN_DB_KEY: str = "ldap_auth"


def _load_plugin_config() -> dict:
    """Load plugin configuration from plugin.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'plugin.json')
    with open(config_path, 'r') as f:
        return json.load(f)


PLUGIN_CONFIG = _load_plugin_config()


# ── Plugin field definitions ─────────────────────────────────────────────────
PLUGIN_FIELDS = [
    # -- Connection -----------------------------------------------------------
    {
        "id": "ldap_server_url",
        "label": "LDAP Server URL",
        "type": "string",
        "default": "",
        "description": (
            "LDAP server URL, e.g. ldap://ldap.example.com or "
            "ldaps://ldap.example.com:636"
        ),
        "placeholder": "ldap://ldap.example.com",
    },
    {
        "id": "use_ssl",
        "label": "Use SSL (LDAPS)",
        "type": "boolean",
        "default": False,
        "description": (
            "Use LDAPS (port 636) instead of plain LDAP. "
            "Ignored if the server URL already specifies ldaps://"
        ),
    },
    {
        "id": "start_tls",
        "label": "Use STARTTLS",
        "type": "boolean",
        "default": False,
        "description": "Upgrade the connection with STARTTLS after connecting on the plain port",
    },

    # -- Bind credentials -----------------------------------------------------
    {
        "id": "bind_dn",
        "label": "Bind DN",
        "type": "string",
        "default": "",
        "description": (
            "DN used for the initial bind (service account). "
            "Leave empty for anonymous bind"
        ),
        "placeholder": "cn=readonly,dc=example,dc=com",
    },
    {
        "id": "bind_password",
        "label": "Bind Password",
        "type": "password",
        "default": "",
        "description": "Password for the bind DN",
    },

    # -- User search ----------------------------------------------------------
    {
        "id": "user_search_base",
        "label": "User Search Base",
        "type": "string",
        "default": "",
        "description": "Base DN for user searches",
        "placeholder": "ou=users,dc=example,dc=com",
    },
    {
        "id": "user_search_filter",
        "label": "User Search Filter",
        "type": "string",
        "default": "(&(objectClass=person)(uid={username}))",
        "description": (
            "LDAP filter to find users. {username} is replaced with the login name. "
            "For Active Directory use: (&(objectClass=user)(sAMAccountName={username}))"
        ),
        "placeholder": "(&(objectClass=person)(uid={username}))",
    },

    # -- Authentication scope -------------------------------------------------
    {
        "id": "enable_ui_auth",
        "label": "Enable UI Login via LDAP",
        "type": "boolean",
        "default": True,
        "description": "Allow LDAP users to log in to the Dispatcharr web UI",
    },
    {
        "id": "enable_xc_auth",
        "label": "Enable XC Auth via LDAP",
        "type": "boolean",
        "default": False,
        "description": (
            "Allow LDAP credentials for Xtream Codes endpoints. "
            "Note: this causes an LDAP bind on every XC request which may add latency"
        ),
    },

    # -- User provisioning ----------------------------------------------------
    {
        "id": "auto_create_users",
        "label": "Auto-Create Users",
        "type": "boolean",
        "default": True,
        "description": (
            "Automatically create a Dispatcharr user on first LDAP login. "
            "If disabled, LDAP users must already exist in Dispatcharr"
        ),
    },
    {
        "id": "default_user_level",
        "label": "Default User Level",
        "type": "select",
        "default": "0",
        "options": [
            {"value": "0", "label": "Streamer"},
            {"value": "1", "label": "Standard"},
            {"value": "10", "label": "Admin"},
        ],
        "description": "User level assigned to auto-created LDAP users",
    },
    {
        "id": "admin_group_dn",
        "label": "Admin Group DN",
        "type": "string",
        "default": "",
        "description": (
            "Members of this LDAP group are created as admins (user_level=10). "
            "Leave empty to use the default user level for everyone"
        ),
        "placeholder": "cn=dispatcharr-admins,ou=groups,dc=example,dc=com",
    },
    {
        "id": "group_membership_attr",
        "label": "Group Membership Attribute",
        "type": "string",
        "default": "memberOf",
        "description": "User attribute containing group DNs (e.g. memberOf for AD/OpenLDAP overlay)",
    },
    {
        "id": "auto_generate_xc_password",
        "label": "Auto-Generate XC Password",
        "type": "boolean",
        "default": True,
        "description": (
            "Generate a random xc_password for auto-created users so they can "
            "use XC endpoints with their assigned credentials"
        ),
    },

    # -- Performance ----------------------------------------------------------
    {
        "id": "cache_ttl",
        "label": "Auth Cache TTL (seconds)",
        "type": "number",
        "default": DEFAULT_CACHE_TTL,
        "description": (
            "Cache successful LDAP authentications for this many seconds to "
            "reduce LDAP bind traffic. Set to 0 to disable caching"
        ),
        "placeholder": "300",
    },

    # -- Diagnostics ----------------------------------------------------------
    {
        "id": "info_section",
        "label": "Diagnostics",
        "type": "info",
        "value": (
            "Use the 'Test Connection' action below to verify LDAP connectivity. "
            "Use 'Test Login' to verify a specific user can authenticate."
        ),
    },
]
