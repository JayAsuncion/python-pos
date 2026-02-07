import strawberry

@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str