from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def is_bcrypt_hash(value: str) -> bool:
    """Check if a string is a bcrypt hash (starts with $2b$ or $2a$)."""
    return value.startswith(("$2b$", "$2a$", "$2y$"))
