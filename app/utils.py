
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # using bcrypt algorithem

def hash(password: str):
     return pwd_context.hash(password)

def varify(plain_password, hashed_password):
     return pwd_context.verify(plain_password, hashed_password)