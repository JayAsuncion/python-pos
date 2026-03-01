from fastapi import Request
from app.auth.jwt import decode_access_token
from app.database import SessionLocal
from app.models.user import User as UserModel


async def get_context(request: Request) -> dict:
    """
    Custom context getter for Strawberry GraphQLRouter.
    Extracts the JWT token from the Authorization header,
    validates it, and loads the user from the database.
    Returns a dict with 'request' and 'user' (or None if not authenticated).
    """
    context = {"request": request, "user": None}

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return context

    token = auth_header.split("Bearer ")[1]
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            return context

        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            context["user"] = user
        finally:
            db.close()
    except ValueError:
        # Invalid token - return context without user
        pass

    return context
