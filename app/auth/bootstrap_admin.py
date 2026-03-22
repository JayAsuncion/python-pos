"""
Bootstrap super admin user.
Run with: python -m app.auth.bootstrap_admin
"""

from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.auth.security import hash_password

def bootstrap_admin():
    """Create the first super admin user if it doesn't exist."""
    db = SessionLocal()
    
    # Check if super admin already exists
    existing_admin = db.query(User).filter(User.username == "superadmin").first()
    if existing_admin:
        print("Super admin user already exists!")
        db.close()
        return
    
    # Create super admin user with hashed password
    admin_user = User(
        username="superadmin",
        email="admin@pos.com",
        first_name="Super",
        last_name="Admin",
        hashed_password=hash_password("changeme123")  # Bcrypt hashed
    )
    db.add(admin_user)
    db.flush()  # Get the user.id
    
    # Get SUPER_ADMIN role
    super_admin_role = db.query(Role).filter(Role.code == "SUPER_ADMIN").first()
    if not super_admin_role:
        print("ERROR: SUPER_ADMIN role not found. Please run seed_permissions first.")
        db.rollback()
        db.close()
        return
    
    # Assign SUPER_ADMIN role to the user
    user_role = UserRole(
        user_id=admin_user.id,
        role_id=super_admin_role.id
    )
    db.add(user_role)
    db.commit()
    
    print(f"✅ Super admin user created successfully!")
    print(f"   Username: superadmin")
    print(f"   Password: changeme123 (please change on first login)")
    print(f"   Email: admin@pos.com")
    
    db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=== Bootstrapping Super Admin User ===")
    bootstrap_admin()
    print("=== Done! ===")
