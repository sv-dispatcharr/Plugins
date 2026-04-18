"""LDAP authentication backend used by the plugin hooks.

Handles:
  - LDAP server connection (plain, SSL, STARTTLS)
  - Service-account bind + user search
  - User bind for credential verification
  - Optional credential caching with TTL
  - JIT user provisioning in Django
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# In-memory auth cache: {cache_key: expiry_timestamp}
# Intentionally simple — cleared on plugin reload / container restart.
_auth_cache: dict = {}


def _cache_key(username: str, password: str) -> str:
    """Derive a cache key from username + password without storing the password."""
    h = hashlib.sha256(f"{username}:{password}".encode("utf-8")).hexdigest()
    return f"ldap_auth:{h}"


def check_cache(username: str, password: str, ttl: int) -> bool:
    """Return True if a recent successful auth is cached and still valid."""
    if ttl <= 0:
        return False
    key = _cache_key(username, password)
    expiry = _auth_cache.get(key)
    if expiry is not None and time.monotonic() < expiry:
        return True
    # Expired — remove stale entry
    _auth_cache.pop(key, None)
    return False


def set_cache(username: str, password: str, ttl: int) -> None:
    """Record a successful auth in the cache."""
    if ttl <= 0:
        return
    key = _cache_key(username, password)
    _auth_cache[key] = time.monotonic() + ttl


def clear_cache() -> None:
    """Wipe the entire auth cache."""
    _auth_cache.clear()


@contextmanager
def _ldap_connection(settings: dict):
    """Yield a bound ldap3 Connection (service-account bind), then unbind."""
    try:
        import ldap3
    except ImportError:
        raise RuntimeError(
            "The ldap3 package is not installed. "
            "Run: pip install ldap3   inside the Dispatcharr container"
        )

    server_url = (settings.get("ldap_server_url") or "").strip()
    if not server_url:
        raise ValueError("LDAP Server URL is not configured")

    use_ssl = settings.get("use_ssl", False)
    # Auto-detect SSL from URL scheme
    if server_url.lower().startswith("ldaps://"):
        use_ssl = True

    server = ldap3.Server(server_url, use_ssl=use_ssl, get_info=ldap3.NONE)

    bind_dn = (settings.get("bind_dn") or "").strip()
    bind_password = settings.get("bind_password") or ""

    conn = ldap3.Connection(
        server,
        user=bind_dn or None,
        password=bind_password or None,
        auto_bind=False,
        raise_exceptions=True,
        read_only=True,
    )

    try:
        conn.bind()
        if settings.get("start_tls", False):
            conn.start_tls()
        yield conn
    finally:
        try:
            conn.unbind()
        except Exception:
            pass


def _find_user_dn(conn, settings: dict, username: str) -> str | None:
    """Search for a user and return their DN, or None if not found."""
    import ldap3

    search_base = (settings.get("user_search_base") or "").strip()
    if not search_base:
        raise ValueError("User Search Base is not configured")

    filter_template = settings.get(
        "user_search_filter",
        "(&(objectClass=person)(uid={username}))",
    )
    search_filter = filter_template.replace("{username}", ldap3.utils.conv.escape_filter_chars(username))

    scope_map = {
        "base": ldap3.BASE,
        "level": ldap3.LEVEL,
        "one": ldap3.LEVEL,
        "subtree": ldap3.SUBTREE,
    }
    scope = scope_map.get(
        (settings.get("search_scope") or "subtree").lower(),
        ldap3.SUBTREE,
    )

    group_attr = (settings.get("group_membership_attr") or "memberOf").strip()
    conn.search(search_base, search_filter, search_scope=scope, attributes=[group_attr])

    if not conn.entries:
        return None

    return conn.entries[0].entry_dn


def _get_user_groups(conn, settings: dict, user_dn: str) -> list[str]:
    """Return a list of group DNs the user belongs to."""
    import ldap3

    group_attr = (settings.get("group_membership_attr") or "memberOf").strip()
    conn.search(user_dn, "(objectClass=*)", search_scope=ldap3.BASE, attributes=[group_attr])

    if not conn.entries:
        return []

    try:
        return list(conn.entries[0][group_attr].values)
    except (KeyError, ldap3.core.exceptions.LDAPKeyError):
        return []


def _bind_as_user(settings: dict, user_dn: str, password: str) -> bool:
    """Attempt a simple bind as the user to verify their password."""
    import ldap3

    server_url = (settings.get("ldap_server_url") or "").strip()
    use_ssl = settings.get("use_ssl", False)
    if server_url.lower().startswith("ldaps://"):
        use_ssl = True

    server = ldap3.Server(server_url, use_ssl=use_ssl, get_info=ldap3.NONE)
    conn = ldap3.Connection(server, user=user_dn, password=password, auto_bind=False)

    try:
        if not conn.bind():
            return False
        if settings.get("start_tls", False):
            conn.start_tls()
        return True
    except Exception:
        return False
    finally:
        try:
            conn.unbind()
        except Exception:
            pass


def authenticate(username: str, password: str, settings: dict):
    """Authenticate a user against LDAP and return a Django User or None.

    Flow:
      1. Check cache → return cached User if hit
      2. Service-account bind → search for user DN
      3. Bind as user → verify password
      4. JIT-create Django User if needed
      5. Cache successful result
    """
    if not username or not password:
        return None

    cache_ttl = int(settings.get("cache_ttl", 300))

    # 1. Cache check
    if check_cache(username, password, cache_ttl):
        return _get_django_user(username)

    # 2-3. LDAP search + bind
    try:
        with _ldap_connection(settings) as conn:
            user_dn = _find_user_dn(conn, settings, username)
            if user_dn is None:
                logger.debug("LDAP: user '%s' not found", username)
                return None

            if not _bind_as_user(settings, user_dn, password):
                logger.debug("LDAP: bind failed for user '%s'", username)
                return None

            # Read group memberships for admin mapping
            groups = []
            admin_group_dn = (settings.get("admin_group_dn") or "").strip()
            if admin_group_dn:
                groups = _get_user_groups(conn, settings, user_dn)

    except Exception:
        logger.error("LDAP authentication error for '%s'", username, exc_info=True)
        return None

    # 4. Get or create Django user
    user = _get_or_create_user(username, settings, groups)
    if user is None:
        return None

    # 5. Cache
    set_cache(username, password, cache_ttl)

    return user


def _get_django_user(username: str):
    """Look up an existing Django User by username."""
    from apps.accounts.models import User
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def _get_or_create_user(username: str, settings: dict, groups: list[str]):
    """Return an existing Django User, or create one if auto_create_users is enabled."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(username=username)
        # Update admin status based on current group membership
        _sync_user_level(user, settings, groups)
        return user
    except User.DoesNotExist:
        pass

    if not settings.get("auto_create_users", True):
        logger.debug("LDAP: user '%s' not in Dispatcharr and auto-create disabled", username)
        return None

    # Determine user level
    user_level = int(settings.get("default_user_level", 0))
    admin_group_dn = (settings.get("admin_group_dn") or "").strip().lower()
    if admin_group_dn and any(g.lower() == admin_group_dn for g in groups):
        user_level = 10

    try:
        user = User.objects.create_user(username=username, password=None)
        user.user_level = user_level

        # Optionally generate xc_password
        if settings.get("auto_generate_xc_password", True):
            props = user.custom_properties or {}
            if "xc_password" not in props:
                props["xc_password"] = secrets.token_urlsafe(24)
                user.custom_properties = props

        user.save()
        logger.info("LDAP: created Dispatcharr user '%s' (level=%d)", username, user_level)
        return user
    except Exception:
        logger.error("LDAP: failed to create user '%s'", username, exc_info=True)
        return None


def _sync_user_level(user, settings: dict, groups: list[str]) -> None:
    """Sync admin/non-admin status based on current LDAP group membership."""
    admin_group_dn = (settings.get("admin_group_dn") or "").strip().lower()
    if not admin_group_dn:
        return

    is_admin = any(g.lower() == admin_group_dn for g in groups)
    if is_admin and user.user_level < 10:
        user.user_level = 10
        user.save(update_fields=["user_level"])
        logger.info("LDAP: promoted '%s' to admin via group membership", user.username)
    elif not is_admin and user.user_level >= 10:
        default_level = int(settings.get("default_user_level", 0))
        user.user_level = default_level
        user.save(update_fields=["user_level"])
        logger.info("LDAP: demoted '%s' to level %d (no longer in admin group)", user.username, default_level)


def test_connection(settings: dict) -> dict:
    """Test LDAP connectivity. Returns a result dict for the plugin action."""
    try:
        with _ldap_connection(settings) as conn:
            return {
                "status": "success",
                "message": (
                    f"Connected to {settings.get('ldap_server_url')} | "
                    f"Bound as: {conn.user or 'anonymous'}"
                ),
            }
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {e}"}


def test_login(username: str, password: str, settings: dict) -> dict:
    """Test a specific user's LDAP authentication. Returns a result dict."""
    if not username or not password:
        return {"status": "error", "message": "Username and password are required"}

    try:
        with _ldap_connection(settings) as conn:
            user_dn = _find_user_dn(conn, settings, username)
            if user_dn is None:
                return {"status": "error", "message": f"User '{username}' not found in LDAP"}

            if not _bind_as_user(settings, user_dn, password):
                return {"status": "error", "message": f"Bind failed for '{username}' (wrong password?)"}

            groups = []
            admin_group_dn = (settings.get("admin_group_dn") or "").strip()
            if admin_group_dn:
                groups = _get_user_groups(conn, settings, user_dn)

            is_admin = admin_group_dn and any(
                g.lower() == admin_group_dn.lower() for g in groups
            )
            level_label = "Admin" if is_admin else f"Level {settings.get('default_user_level', 0)}"

            return {
                "status": "success",
                "message": (
                    f"User '{username}' authenticated successfully | "
                    f"DN: {user_dn} | "
                    f"Groups: {len(groups)} | "
                    f"Would be: {level_label}"
                ),
            }
    except Exception as e:
        return {"status": "error", "message": f"Test failed: {e}"}
