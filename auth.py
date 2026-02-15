import os
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET=os.getenv("JWT_SECRET")
pwd=CryptContext(schemes=["bcrypt"])

def hash_pw(p):
    return pwd.hash(p)

def verify_pw(p,h):
    return pwd.verify(p,h)

def create_token(email):
    return jwt.encode({"email":email},SECRET,algorithm="HS256")

def get_email(token):
    return jwt.decode(token,SECRET,algorithms=["HS256"])["email"]