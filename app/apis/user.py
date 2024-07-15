from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import DB_Session

from cruds import UserCRUD
from models import UserModel

from schemas import UserCreateSchema, UserUpdateSchema


router = APIRouter()
crud = UserCRUD(UserModel)

@router.post("/", 
        summary="create user")
async def create_user(
    user_create: UserCreateSchema, 
    db_session: Session = Depends(DB_Session())
):
    result = crud.create(db_session=db_session, create_info=user_create)
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="create user failed")
    
@router.delete("/{id}", 
        summary="delete user by id")
async def delete_user(
    id: int,
    db_session: Session = Depends(DB_Session())
):
    user = crud.retrieve(db_session=db_session, item_id=id)
    if user:
        result = crud.delete(db_session=db_session, item_to_delete=user)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="delete user failed")
    else:
        raise HTTPException(status_code=400, detail="user not found")
    
@router.delete("/multi", 
        summary="delete users by id")
async def delete_user(
    id_list: list[int],
    db_session: Session = Depends(DB_Session())
):
    delete_failed_list: list[int] = []
    user_unfind_list: list[int] = []
    for id in id_list:
        user = crud.retrieve(db_session=db_session, item_id=id)
        if user:
            result = crud.delete(db_session=db_session, item_to_delete=user)
            if not result:
                delete_failed_list.append(id)
        else:
            user_unfind_list.append(id)
    if not delete_failed_list and not user_unfind_list:
        return True
    else:
        raise HTTPException(status_code=400, 
                            detail=f"delete user failed: {delete_failed_list}, user not found: {user_unfind_list}")
    
@router.put("/", 
            summary=f"update user info")
async def update_user(
    user_update: UserUpdateSchema,
    db_session: Session = Depends(DB_Session())
):
    user = crud.retrieve(db_session=db_session, item_id=user_update.id)
    if user:
        result = crud.update(db_session=db_session, item_to_update=user, update_info=user_update)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="update user failed")
    else:
        raise HTTPException(status_code=400, detail="user not found")

@router.get("/mutil",
            summary="get user list")
async def get_user_list(
    skip: int = 0,
    limit: int = 20,
    db_session: Session = Depends(DB_Session())
):
    results = crud.retrieve_mutil(db_session=db_session, skip=skip, limit=limit)
    if results:
        return results
    else:
        raise HTTPException(status_code=400, detail="user not found")
    
@router.get("/{id}",
            summary="get user info")
async def get_user(
    id: int,
    db_session: Session = Depends(DB_Session())
):
    result = crud.retrieve(db_session=db_session, item_id=id)
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="user not found")