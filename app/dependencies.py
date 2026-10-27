import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import SECRET_KEY, ALGORITHM
from .database import get_db
from .models import User


bearer_scheme = HTTPBearer()

def get_current_user(
        credentials : HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms= [ALGORITHM]
        )

        user_id = int(payload["sub"])


    except(InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials",
            headers = {"WWW-Authenticate": "Bearer"}

        )

    user = db.query(User).filter( user_id == User.id).first()


    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found",
            headers = {"WWW-Authenticate": "Bearer"},
            
        )
    return user
