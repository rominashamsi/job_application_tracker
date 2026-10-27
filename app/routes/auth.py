

import jwt
from ..config import SECRET_KEY, ALGORITHM
from datetime import datetime,timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreate, UserResponse, UserLogin, Token , PasswordChange
from ..models import User
from pwdlib import PasswordHash
from ..dependencies import get_current_user 




def create_access_token(user_id:int) -> str :
    payload = {
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) +timedelta(minutes=30)
    }
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm = ALGORITHM
    )
    return token




router= APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
password_hash= PasswordHash.recommended()

@router.post("/register",
             response_model= UserResponse,
             status_code= 201)
def register(user_data : UserCreate, db: Session = Depends(get_db)):
    existing_user=db.query(User).filter(
        User.email== user_data.email
    ).first()


    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(user_data.password)

    new_user = User(
        name = user_data.name,
        email = user_data.email,
        hashed_password = hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)



    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
        }





@router.post("/login",
             response_model = Token,
             status_code=200)
def login(user_data:UserLogin,
          db:Session =Depends(get_db)):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if user is None or not password_hash.verify(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
        }




@router.get("/me", response_model= UserResponse)
def read_current_user(current_user : User = Depends(get_current_user)):
    return{
        "id" : current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }




@router.patch("/password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not password_hash.verify(
        password_data.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = password_hash.hash(
        password_data.new_password
    )

    db.commit()

    return {"message": "Password changed successfully"}





    