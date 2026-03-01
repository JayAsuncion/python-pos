import strawberry
from typing import Optional
from app.models.user import User as UserModel
from app.schemas.auth import AuthPayloadType, TokenType
from app.schemas.user import UserType
from app.auth.security import verify_password, is_bcrypt_hash, hash_password
from app.auth.jwt import create_access_token
from app.auth.permissions import require_auth
from app.database import SessionLocal


@strawberry.type
class AuthMutations:
    @strawberry.mutation(name="login")
    def login(self, username: str, password: str) -> AuthPayloadType:
        db = SessionLocal()
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            db.close()
            raise ValueError("Invalid username or password")

        requires_reset = False

        if is_bcrypt_hash(user.hashed_password):
            # Password is properly hashed - verify with bcrypt
            if not verify_password(password, user.hashed_password):
                db.close()
                raise ValueError("Invalid username or password")
        else:
            # Password is plaintext (legacy) - compare directly
            if password != user.hashed_password:
                db.close()
                raise ValueError("Invalid username or password")
            requires_reset = True

        db.close()

        # Create JWT token
        token_data = {"sub": user.username, "user_id": user.id}
        access_token = create_access_token(data=token_data)

        return AuthPayloadType(
            token=TokenType(access_token=access_token, token_type="bearer"),
            user=UserType(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ),
            requires_password_reset=requires_reset,
        )

    @strawberry.mutation(name="resetPassword")
    def reset_password(
        self, info: strawberry.types.Info, old_password: str, new_password: str
    ) -> bool:
        user = require_auth(info)
        db = SessionLocal()

        db_user = db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            db.close()
            raise ValueError("User not found")

        # Verify old password (handle both plaintext and hashed)
        if is_bcrypt_hash(db_user.hashed_password):
            if not verify_password(old_password, db_user.hashed_password):
                db.close()
                raise ValueError("Old password is incorrect")
        else:
            if old_password != db_user.hashed_password:
                db.close()
                raise ValueError("Old password is incorrect")

        # Hash and save new password
        db_user.hashed_password = hash_password(new_password)
        db.commit()
        db.close()
        return True

    @strawberry.mutation(name="changeUserPassword")
    def change_user_password(
        self, info: strawberry.types.Info, user_id: int, new_password: str
    ) -> bool:
        """Admin-only: Reset another user's password. Requires UPDATE_USER permission."""
        from app.auth.permissions import require_permission

        require_permission(info, "UPDATE_USER")
        db = SessionLocal()

        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            db.close()
            raise ValueError(f"User with id {user_id} not found")

        db_user.hashed_password = hash_password(new_password)
        db.commit()
        db.close()
        return True
