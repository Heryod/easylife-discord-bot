import json
import os
from datetime import datetime
from loguru import logger
from typing import Optional, List, Dict, Any

ROLES_FILE = "data/roles.json"


def _ensure_file_exists():
    """Ensures the roles.json file exists."""
    if not os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, "w") as f:
            json.dump([], f, indent=4)
        logger.info(f"Created {ROLES_FILE}")


def _load_roles() -> List[Dict[str, Any]]:
    """Loads all roles from the JSON file."""
    try:
        _ensure_file_exists()
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading roles from {ROLES_FILE}: {e}")
        return []


def _save_roles(roles: List[Dict[str, Any]]):
    """Saves roles to the JSON file."""
    try:
        with open(ROLES_FILE, "w") as f:
            json.dump(roles, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving roles to {ROLES_FILE}: {e}")


def save_role(
    user_id: int,
    role_id: int,
    role_name: str,
    granted_by: int,
    granted_by_name: str,
    expiration_time: Optional[str] = None,
) -> bool:
    """
    Saves a role assignment to the JSON file.
    """
    try:
        roles = _load_roles()

        if any(r["user_id"] == user_id and r["role_id"] == role_id for r in roles):
            logger.warning(f"User {user_id} already has role {role_id}")
            return False

        role_entry = {
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "granted_by": granted_by,
            "granted_by_name": granted_by_name,
            "granted_at": datetime.now().isoformat(),
            "expires_at": expiration_time,
        }

        roles.append(role_entry)
        _save_roles(roles)
        logger.info(f"Saved role {role_name} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving role: {e}")
        return False


def remove_role(user_id: int, role_id: int) -> bool:
    """
    Removes a role assignment from the JSON file.

    """
    try:
        roles = _load_roles()
        original_count = len(roles)
        roles = [r for r in roles if not (r["user_id"] == user_id and r["role_id"] == role_id)]

        if len(roles) == original_count:
            logger.warning(f"Role {role_id} for user {user_id} not found")
            return False

        _save_roles(roles)
        logger.info(f"Removed role {role_id} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error removing role: {e}")
        return False


def get_user_roles(user_id: int) -> List[Dict[str, Any]]:
    """Gets all roles assigned to a user."""
    try:
        roles = _load_roles()
        return [r for r in roles if r["user_id"] == user_id]
    except Exception as e:
        logger.error(f"Error getting roles for user {user_id}: {e}")
        return []


def get_role(user_id: int, role_id: int) -> Optional[Dict[str, Any]]:
    """Gets a specific role assignment."""
    try:
        roles = _load_roles()
        for r in roles:
            if r["user_id"] == user_id and r["role_id"] == role_id:
                return r
        return None
    except Exception as e:
        logger.error(f"Error getting role for user {user_id}: {e}")
        return None


def get_expired_roles() -> List[Dict[str, Any]]:
    """Gets all roles that have expired."""
    try:
        roles = _load_roles()
        expired = []
        now = datetime.now()

        for role in roles:
            if role.get("expires_at"):
                try:
                    expiration = datetime.fromisoformat(role["expires_at"])
                    if expiration <= now:
                        expired.append(role)
                except Exception as e:
                    logger.error(f"Error parsing expiration time for role {role.get('role_id')}: {e}")

        return expired

    except Exception as e:
        logger.error(f"Error getting expired roles: {e}")
        return []


def remove_expired_roles() -> List[Dict[str, Any]]:
    """Removes all expired roles and returns them."""
    try:
        expired = get_expired_roles()
        if not expired:
            return []

        roles = _load_roles()
        for expired_role in expired:
            roles = [r for r in roles if not (r["user_id"] == expired_role["user_id"] and r["role_id"] == expired_role["role_id"])]

        _save_roles(roles)
        logger.info(f"Removed {len(expired)} expired roles")
        return expired

    except Exception as e:
        logger.error(f"Error removing expired roles: {e}")
        return []


def get_all_roles() -> List[Dict[str, Any]]:
    """Gets all roles from the file."""
    return _load_roles()
