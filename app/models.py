from datetime import datetime
from typing import Any, TypeVar
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql.sqltypes import TypeEngine
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Boolean
from passlib.context import CryptContext


class BaseModel(AsyncAttrs, DeclarativeBase):

    __abstract__ = True

    id:  Mapped[int] = mapped_column(Integer, primary_key=True, comment='主键ID')
    create_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment='创建时间')
    update_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    delete_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='删除时间')
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否软删除")


class UserModel(BaseModel):

    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(256), nullable=False, comment="密码")
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="邮箱地址")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="账号禁用")



ModelType = TypeVar("ModelType", bound=BaseModel)