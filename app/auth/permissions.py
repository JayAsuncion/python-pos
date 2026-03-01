import strawberry
from app.database import SessionLocal
from app.models.user import User as UserModel


def get_user_permissions(db, user_id: int) -> set:
    """
    Get all permission codes for a user by traversing:
    User -> UserRole -> Role -> RolePermission -> Permission
    Only includes active (non-deleted) records.
    """
    from app.models.user_role import UserRole
    from app.models.role_permission import RolePermission
    from app.models.permission import Permission

    results = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .filter(
            UserRole.user_id == user_id,
            UserRole.deleted_at.is_(None),
            RolePermission.deleted_at.is_(None),
            Permission.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    return {row[0] for row in results}


def require_permission(info: strawberry.types.Info, permission_code: str) -> UserModel:
    """
    Validate that the current user (from context) has the required permission.
    Returns the authenticated user if authorized.
    Raises ValueError if not authenticated or not authorized.
    """
    user = info.context.get("user")
    if not user:
        raise ValueError("Authentication required. Please provide a valid token in the Authorization header.")

    db = SessionLocal()
    try:
        permissions = get_user_permissions(db, user.id)
    finally:
        db.close()

    if permission_code not in permissions:
        raise ValueError(f"Permission denied. Required permission: {permission_code}")

    return user


def require_auth(info: strawberry.types.Info) -> UserModel:
    """
    Validate that the request has a valid authenticated user.
    Returns the user. Raises ValueError if not authenticated.
    """
    user = info.context.get("user")
    if not user:
        raise ValueError("Authentication required. Please provide a valid token in the Authorization header.")
    return user
