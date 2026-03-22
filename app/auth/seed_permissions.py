"""
Seed script for permissions and default roles.
Run with: python -m app.auth.seed_permissions
"""

from app.database import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

# (code, name, description, category)
BASE_PERMISSIONS = [
    # User
    ("VIEW_USER", "View Users", "Can view user list and details", "USER"),
    ("CREATE_USER", "Create User", "Can create new users", "USER"),
    ("UPDATE_USER", "Update User", "Can update user details", "USER"),
    ("DELETE_USER", "Delete User", "Can delete users", "USER"),
    # Product
    ("VIEW_PRODUCT", "View Products", "Can view product list and details", "PRODUCT"),
    ("CREATE_PRODUCT", "Create Product", "Can create new products", "PRODUCT"),
    ("UPDATE_PRODUCT", "Update Product", "Can update product details", "PRODUCT"),
    ("DELETE_PRODUCT", "Delete Product", "Can delete products", "PRODUCT"),
    # ProductTemplate
    ("VIEW_PRODUCT_TEMPLATE", "View Product Templates", "Can view product template list and details", "PRODUCT_TEMPLATE"),
    ("CREATE_PRODUCT_TEMPLATE", "Create Product Template", "Can create new product templates", "PRODUCT_TEMPLATE"),
    ("UPDATE_PRODUCT_TEMPLATE", "Update Product Template", "Can update product template details", "PRODUCT_TEMPLATE"),
    ("DELETE_PRODUCT_TEMPLATE", "Delete Product Template", "Can delete product templates", "PRODUCT_TEMPLATE"),
    # ProductSlot
    ("VIEW_PRODUCT_SLOT", "View Product Slots", "Can view product slot list and details", "PRODUCT_SLOT"),
    ("CREATE_PRODUCT_SLOT", "Create Product Slot", "Can create new product slots", "PRODUCT_SLOT"),
    ("UPDATE_PRODUCT_SLOT", "Update Product Slot", "Can update product slot details", "PRODUCT_SLOT"),
    ("DELETE_PRODUCT_SLOT", "Delete Product Slot", "Can delete product slots", "PRODUCT_SLOT"),
    # ProductSlotReading
    ("VOID_PRODUCT_SLOT_READING", "Void Product Slot Reading", "Can void product slot readings", "PRODUCT_SLOT_READING"),
    # Shift
    ("VIEW_SHIFT", "View Shifts", "Can view shift list and details", "SHIFT"),
    ("START_SHIFT", "Start Shift", "Can start a new shift", "SHIFT"),
    ("END_SHIFT", "End Shift", "Can end an active shift", "SHIFT"),
    ("DELETE_SHIFT", "Delete Shift", "Can delete shifts", "SHIFT"),
    # ShiftTemplate
    ("VIEW_SHIFT_TEMPLATE", "View Shift Templates", "Can view shift template list and details", "SHIFT_TEMPLATE"),
    ("CREATE_SHIFT_TEMPLATE", "Create Shift Template", "Can create new shift templates", "SHIFT_TEMPLATE"),
    ("UPDATE_SHIFT_TEMPLATE", "Update Shift Template", "Can update shift template details", "SHIFT_TEMPLATE"),
    ("DELETE_SHIFT_TEMPLATE", "Delete Shift Template", "Can delete shift templates", "SHIFT_TEMPLATE"),
    # ShiftUser
    ("DELETE_SHIFT_USER", "Delete Shift User", "Can delete shift user assignments", "SHIFT_USER"),
    # Permission (RBAC management)
    ("VIEW_PERMISSION", "View Permissions", "Can view permission list", "RBAC"),
    ("CREATE_PERMISSION", "Create Permission", "Can create new permissions", "RBAC"),
    ("UPDATE_PERMISSION", "Update Permission", "Can update permissions", "RBAC"),
    ("DELETE_PERMISSION", "Delete Permission", "Can delete permissions", "RBAC"),
    # Role (RBAC management)
    ("VIEW_ROLE", "View Roles", "Can view role list", "RBAC"),
    ("CREATE_ROLE", "Create Role", "Can create new roles", "RBAC"),
    ("UPDATE_ROLE", "Update Role", "Can update roles", "RBAC"),
    ("DELETE_ROLE", "Delete Role", "Can delete roles", "RBAC"),
    # UserRole (RBAC management)
    ("VIEW_USER_ROLE", "View User Roles", "Can view user role assignments", "RBAC"),
    ("ASSIGN_ROLE", "Assign Role", "Can assign roles to users", "RBAC"),
    ("REVOKE_ROLE", "Revoke Role", "Can revoke roles from users", "RBAC"),
    # RolePermission (RBAC management)
    ("VIEW_ROLE_PERMISSION", "View Role Permissions", "Can view role permission assignments", "RBAC"),
    ("GRANT_PERMISSION", "Grant Permission", "Can grant permissions to roles", "RBAC"),
    ("REVOKE_PERMISSION", "Revoke Permission", "Can revoke permissions from roles", "RBAC"),
]

# Default roles: (code, name, description, permission_codes)
DEFAULT_ROLES = [
    (
        "SUPER_ADMIN",
        "Super Administrator",
        "Full system access with all permissions",
        None,  # None means ALL permissions
    ),
    (
        "MANAGER",
        "Manager",
        "Can manage products, shifts, templates, and view reports",
        [
            "VIEW_USER", "VIEW_PRODUCT", "CREATE_PRODUCT", "UPDATE_PRODUCT", "DELETE_PRODUCT",
            "VIEW_PRODUCT_TEMPLATE", "CREATE_PRODUCT_TEMPLATE", "UPDATE_PRODUCT_TEMPLATE", "DELETE_PRODUCT_TEMPLATE",
            "VIEW_PRODUCT_SLOT", "CREATE_PRODUCT_SLOT", "UPDATE_PRODUCT_SLOT", "DELETE_PRODUCT_SLOT",
            "VIEW_SHIFT", "START_SHIFT", "END_SHIFT", "DELETE_SHIFT",
            "VIEW_SHIFT_TEMPLATE", "CREATE_SHIFT_TEMPLATE", "UPDATE_SHIFT_TEMPLATE", "DELETE_SHIFT_TEMPLATE",
            "DELETE_SHIFT_USER", "VOID_PRODUCT_SLOT_READING",
        ],
    ),
    (
        "CASHIER",
        "Cashier",
        "Can view products and manage shifts",
        [
            "VIEW_PRODUCT", "VIEW_PRODUCT_TEMPLATE", "VIEW_PRODUCT_SLOT",
            "VIEW_SHIFT", "START_SHIFT", "END_SHIFT",
            "VIEW_SHIFT_TEMPLATE",
        ],
    ),
    (
        "VIEWER",
        "Viewer",
        "Read-only access to products and shifts",
        [
            "VIEW_PRODUCT", "VIEW_PRODUCT_TEMPLATE", "VIEW_PRODUCT_SLOT",
            "VIEW_SHIFT", "VIEW_SHIFT_TEMPLATE",
        ],
    ),
]


def seed_permissions():
    """Seed base permissions into the database. Skips existing ones."""
    db = SessionLocal()
    created_count = 0
    for code, name, description, category in BASE_PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == code).first()
        if not existing:
            permission = Permission(code=code, name=name, description=description, category=category)
            db.add(permission)
            created_count += 1
    db.commit()
    db.close()
    print(f"Seeded {created_count} new permissions ({len(BASE_PERMISSIONS)} total defined)")


def seed_default_roles():
    """Seed default roles and assign permissions. Updates existing roles with new permissions."""
    db = SessionLocal()
    all_permissions = {p.code: p.id for p in db.query(Permission).all()}
    created_count = 0
    updated_count = 0

    for code, name, description, permission_codes in DEFAULT_ROLES:
        existing = db.query(Role).filter(Role.code == code).first()
        
        if not existing:
            # Create new role
            role = Role(code=code, name=name, description=description, is_system_role=True)
            db.add(role)
            db.flush()  # Get the role.id
            
            # Assign permissions
            if permission_codes is None:
                # Assign ALL permissions
                codes_to_assign = list(all_permissions.keys())
            else:
                codes_to_assign = permission_codes
            
            for perm_code in codes_to_assign:
                if perm_code in all_permissions:
                    role_perm = RolePermission(role_id=role.id, permission_id=all_permissions[perm_code])
                    db.add(role_perm)
            
            db.commit()
            created_count += 1
            print(f"  Created role '{code}' with {len(codes_to_assign)} permissions")
        else:
            # Update existing role
            # Determine what permissions should be assigned
            if permission_codes is None:
                # ALL permissions
                expected_perm_codes = set(all_permissions.keys())
            else:
                expected_perm_codes = set(permission_codes)
            
            # Get current permissions for this role
            current_role_perms = db.query(RolePermission).filter(
                RolePermission.role_id == existing.id
            ).all()
            current_perm_ids = {rp.permission_id for rp in current_role_perms}
            
            # Get permission IDs from codes
            expected_perm_ids = {all_permissions[code] for code in expected_perm_codes if code in all_permissions}
            
            # Find missing permissions
            missing_perm_ids = expected_perm_ids - current_perm_ids
            
            if missing_perm_ids:
                # Add missing permissions
                for perm_id in missing_perm_ids:
                    role_perm = RolePermission(role_id=existing.id, permission_id=perm_id)
                    db.add(role_perm)
                
                db.commit()
                updated_count += 1
                print(f"  Updated role '{code}' - added {len(missing_perm_ids)} new permissions")

    db.close()
    print(f"Seeded {created_count} new roles, updated {updated_count} existing roles ({len(DEFAULT_ROLES)} total defined)")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=== Seeding Permissions ===")
    seed_permissions()
    print("\n=== Seeding Default Roles ===")
    seed_default_roles()
    print("\n=== Done! ===")
