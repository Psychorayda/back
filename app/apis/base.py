from typing import Type, TypeVar, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import *

from cruds import CRUDType
from schemas import CreateSchemaType, UpdateSchemaType, RetrieveSchemaType
from models import ModelType

from cruds import *
from models import *
from schemas import *

# from .user import router as user
from .auth import router as auth
from .websocket import router as ws
from .teles import router as teles
from .test import router as test


def base_router(crud: Type[CRUDType], 
                model: Type[ModelType], 
                create_schema: Type[CreateSchemaType], 
                update_schema: Type[UpdateSchemaType]) -> APIRouter:
    router = APIRouter()
    crud = crud(model)

    @router.post("/", 
                summary=f"create {model.__tablename__}")
    async def create(
        item_create: create_schema, 
        db_session: Session = Depends(DB_Session())
    ):
        result = crud.create(db_session=db_session, create_info=item_create)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail=f"create {model.__tablename__} failed")

    @router.delete("/multi", 
                    summary=f"delete multi {model.__tablename__}s by id")
    async def delete_multi(
        id_list: list[int],
        db_session: Session = Depends(DB_Session())
    ):
        delete_failed_list: list[int] = []
        item_unfind_list: list[int] = []
        for id in id_list:
            item = crud.retrieve(db_session=db_session, item_id=id)
            if item:
                result = crud.delete(db_session=db_session, item_to_delete=item)
                if not result:
                    delete_failed_list.append(id)
            else:
                item_unfind_list.append(id)
        if not delete_failed_list and not item_unfind_list:
            return True
        else:
            raise HTTPException(status_code=400, 
                                detail=f"delete {model.__tablename__} failed: {delete_failed_list}, {model.__tablename__} not found: {item_unfind_list}") 

    @router.delete("/{id}", 
                    summary=f"delete {model.__tablename__} by id")
    async def delete(
        id: int,
        db_session: Session = Depends(DB_Session())
    ):
        item = crud.retrieve(db_session=db_session, item_id=id)
        if item:
            result = crud.delete(db_session=db_session, item_to_delete=item)
            if result:
                return result
            else:
                raise HTTPException(status_code=400, detail=f"delete {model.__tablename__} failed")
        else:
            raise HTTPException(status_code=400, detail=f"{model.__tablename__} not found")

    @router.put("/", 
                summary=f"update {model.__tablename__} info")
    async def update(
        item_update: update_schema,
        db_session: Session = Depends(DB_Session())
    ):
        item = crud.retrieve(db_session=db_session, item_id=item_update.id)
        if item:
            result = crud.update(db_session=db_session, item_to_update=item, update_info=item_update)
            if result:
                return result
            else:
                raise HTTPException(status_code=400, detail=f"update {model.__tablename__} failed")
        else:
            raise HTTPException(status_code=400, detail=f"{model.__tablename__} not found")

    @router.get("/mutil",
                summary=f"get mutil {model.__tablename__}s")
    async def get_mutil(
        skip: int = 0,
        limit: int = 20,
        db_session: Session = Depends(DB_Session())
    ):
        results = crud.retrieve_mutil(db_session=db_session, skip=skip, limit=limit)
        return results

    @router.get("/{id}",
                summary=f"get {model.__tablename__} info")
    async def get(
        id: int,
        db_session: Session = Depends(DB_Session())
    ):
        result = crud.retrieve(db_session=db_session, item_id=id)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail=f"{model.__tablename__} not found")

    return router


user = base_router(crud=UserCRUD,  model=UserModel, create_schema=UserCreateSchema, update_schema=UserUpdateSchema)
role = base_router(crud=RoleCRUD,  model=RoleModel, create_schema=RoleCreateSchema, update_schema=RoleUpdateSchema)
perm = base_router(crud=PermCRUD,  model=PermModel, create_schema=PermCreateSchema, update_schema=PermUpdateSchema)
user_role = base_router(crud=UserRoleCRUD,  model=UserRoleModel, create_schema=UserRoleCreateSchema, update_schema=UserRoleUpdateSchema)
role_perm = base_router(crud=RolePermCRUD,  model=RolePermModel, create_schema=RolePermCreateSchema, update_schema=RolePermUpdateSchema)


api_list = [
    {"router": test, "prefix": "/test", "tags": ["Test"], "dependencies": [Depends(TokenChecker())]},
    {"router": auth, "prefix": "/auth", "tags": ["Auth"], "dependencies": []},
    {"router": teles, "prefix": "/teles", "tags": ["Teles"], "dependencies": []},
    {"router": user, "prefix": "/user", "tags": ["User"], "dependencies": []},
    {"router": role, "prefix": "/role", "tags": ["Role"], "dependencies": []},
    {"router": perm, "prefix": "/perm", "tags": ["Perm"], "dependencies": []},
    {"router": user_role, "prefix": "/userrole", "tags": ["UserRole"], "dependencies": []},
    {"router": role_perm, "prefix": "/roleperm", "tags": ["RolePerm"], "dependencies": []},
    {"router": ws, "prefix": "/ws", "tags": ["Websocket"], "dependencies": []},
]