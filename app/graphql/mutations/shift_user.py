import strawberry
from typing import Optional
from sqlalchemy import func
from app.auth.permissions import require_permission
from app.models.shift_user import ShiftUser as ShiftUserModel
from app.schemas.shift_user import ShiftUserType
from app.database import SessionLocal


@strawberry.type
class ShiftUserMutations:
    @strawberry.mutation(name="deleteShiftUser")
    def delete_shift_user(self, info: strawberry.types.Info, shift_user_id: int, deleted_by: int) -> Optional[ShiftUserType]:
        require_permission(info, "DELETE_SHIFT_USER")
        db = SessionLocal()
        db_shift_user = db.query(ShiftUserModel).filter(ShiftUserModel.id == shift_user_id).first()
        if db_shift_user:
            # Soft delete
            db_shift_user.deleted_at = func.now()
            db_shift_user.deleted_by = deleted_by
            db.commit()
            db.refresh(db_shift_user)
            result = ShiftUserType(
                id=db_shift_user.id,
                shift_id=db_shift_user.shift_id,
                user_id=db_shift_user.user_id,
                deleted_at=db_shift_user.deleted_at,
                deleted_by=db_shift_user.deleted_by,
                created_at=db_shift_user.created_at,
                created_by=db_shift_user.created_by,
                updated_at=db_shift_user.updated_at,
                updated_by=db_shift_user.updated_by
            )
        else:
            result = None
        db.close()
        return result
