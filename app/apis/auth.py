from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from dependencies import DB_Session
from models import UserModel
from cruds import UserCRUD
from schemas import UserOutSchema, UserLoginSchema, TokenSchema
from settings import ALGORITHM, SECRET_KEY


router = APIRouter()
crud = UserCRUD(UserModel)

@router.post("/login", 
        response_model=UserOutSchema,
        summary="user login by name password")
async def user_login(
    login_user: UserLoginSchema, 
    db_session: Session = Depends(DB_Session())
):
    user = crud.retrieve_by_name(db_session=db_session, name=login_user.name)
    if user:
        if user.password == login_user.password:
            return jsonable_encoder(user)
        raise HTTPException(status_code=401, detail="Password is incorrect")
    raise HTTPException(status_code=404, detail=f"No user by name: {login_user.name}")

@router.post("/token",
        response_model=TokenSchema,
        summary=["user get token by name password"])
async def get_access_token(
    user_auth: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(DB_Session())
):
    user = crud.retrieve_by_name(db_session=db_session, name=user_auth.username)
    if user:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        payload = {
            "exp": expire,
            "id": user.id
        }
        return TokenSchema(access_token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), token_type="bearer")
    else:
        raise HTTPException(status_code=404, detail=f"No user by name: {user_auth.username}")