import jwt
from passlib.context import CryptContext

passwd_context = CryptContext(
    schemes=['bcrypt']
)


def hashpassword(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return passwd_context.verify(password, hashed_password)