from typing import Type, TypeVar, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import DB_Session

from cruds import CRUDType
from schemas import CreateSchemaType, UpdateSchemaType, RetrieveSchemaType
from models import ModelType

from .user import router as user


def base_router(crud: Type[CRUDType], 
                      model: Type[ModelType], 
                      response_model: Type[RetrieveSchemaType], 
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
                response_model=list[response_model],
                summary=f"get mutil {model.__tablename__}s")
    async def get_mutil(
        skip: int = 0,
        limit: int = 20,
        db_session: Session = Depends(DB_Session())
    ):
        results = crud.retrieve_mutil(db_session=db_session, skip=skip, limit=limit)
        return results

    @router.get("/{id}",
                response_model=response_model,
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


api_list = [
    {"router": user, "prefix": "/user", "tags": ["User"], "dependencies": []},
]