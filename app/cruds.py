from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional, Generic, TypeVar, Type

from models import ModelType
from schemas import CreateSchemaType, UpdateSchemaType

from models import *
from schemas import *


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db_session: Session, create_info: Type[CreateSchemaType]) -> bool:
        try: 
            create_info = jsonable_encoder(create_info)
            item_to_create = self.model(**create_info)
            db_session.add(item_to_create)
            db_session.commit()
            return True
        except Exception as error_info:
            db_session.rollback()
            return False

    def delete(self, db_session: Session, item_to_delete: Type[ModelType]) -> bool:
        try:
            db_session.delete(item_to_delete)
            db_session.commit()
            return True
        except Exception as error_info:
            db_session.rollback()
            return False

    def update(self, db_session: Session, item_to_update: Type[ModelType], update_info: Type[UpdateSchemaType]) -> bool:
        try:
            data_to_update = update_info.dict(exclude_unset=True)
            for colum, value in data_to_update.items():
                setattr(item_to_update, colum, value)
            db_session.add(item_to_update)
            db_session.commit()
            db_session.refresh(item_to_update)
            return True
        except Exception as error_info:
            db_session.rollback()
            return False

    def retrieve(self, db_session: Session, item_id: int) -> Optional[ModelType]:
        try:
            result = db_session.query(self.model).filter(self.model.id == item_id).first()
            return result
        except Exception as error_info:
            db_session.rollback()
            return None

    def retrieve_mutil(self, db_session: Session, skip: int = 0, limit: int = 20) -> List[ModelType]:
        try:
            result_list = db_session.query(self.model).offset(skip).limit(limit).all()
            return result_list
        except Exception as error_info:
            db_session.rollback()
            return []
        

CRUDType = TypeVar("CRUDType", bound=BaseCRUD)


class UserCRUD(BaseCRUD[UserModel, UserCreateSchema, UserUpdateSchema]):
    def retrieve_by_name(self, db_session: Session, name: str) -> Optional[UserModel]:
        try:
            user = db_session.query(self.model).filter(self.model.name == name).first()
            return user
        except Exception as error_info:
            db_session.rollback()
            return None


class RoleCRUD(BaseCRUD[RoleModel, RoleCreateSchema, RoleUpdateSchema]):
    pass


class PermCRUD(BaseCRUD[PermModel, PermCreateSchema, PermUpdateSchema]):
    pass


class UserRoleCRUD(BaseCRUD[UserRoleModel, UserRoleCreateSchema, UserRoleUpdateSchema]):
    pass


class RolePermCRUD(BaseCRUD[RolePermModel, RolePermCreateSchema, RolePermUpdateSchema]):
    pass
        