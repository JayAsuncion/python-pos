import strawberry
from app.schemas.user import UserType


@strawberry.type
class TokenType:
    access_token: str
    token_type: str


@strawberry.type
class AuthPayloadType:
    token: TokenType
    user: UserType
    requires_password_reset: bool
