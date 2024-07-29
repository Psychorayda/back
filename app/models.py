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
    # delete_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='删除时间')
    # is_delete: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否软删除")

ModelType = TypeVar("ModelType", bound=BaseModel)


class UserModel(BaseModel):

    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(256), nullable=False, comment="密码")
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="邮箱地址")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="账号禁用")

    roles = relationship("RoleModel", secondary="user_role", overlaps="users")


class RoleModel(BaseModel):

    __tablename__ = 'role'

    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="角色名")
    desc: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="角色描述")
    
    users = relationship("UserModel", secondary="user_role", overlaps="roles")
    menus = relationship("PermModel", secondary="role_perm", overlaps="roles")


class PermModel(BaseModel):

    __tablename__ = 'perm'

    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="权限名")
    desc: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="权限描述")

    roles = relationship("RoleModel", secondary="role_perm", overlaps="perms")


class UserRoleModel(BaseModel):

    __tablename__ = "user_role"

    user_id = Column(Integer, ForeignKey("user.id"))
    role_id = Column(Integer, ForeignKey("role.id"))


class RolePermModel(BaseModel):

    __tablename__ = "role_perm"

    role_id = Column(Integer, ForeignKey("role.id"))
    perm_id = Column(Integer, ForeignKey("perm.id"))


class SystemLogModel(BaseModel):

    __tablename__ = 'system_log'

    levelname: Mapped[str] = mapped_column(String(16), nullable=False, comment="日志等级")
    message: Mapped[str] = mapped_column(String(1024), nullable=False, comment="日志信息")
    filename: Mapped[str] = mapped_column(String(32), nullable=False, comment="文件名")
    funcName: Mapped[str] = mapped_column(String(64), nullable=False, comment="函数名")
    lineno: Mapped[int] = mapped_column(Integer, nullable=False, comment="代码行号")
    req_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="请求ID")


class RequestLogModel(BaseModel):

    __tablename__ = 'request_log'

    user: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="用户名")
    role: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="角色名")
    host: Mapped[str] = mapped_column(String(64), nullable=False, comment="主机名")
    method: Mapped[str] = mapped_column(String(8), nullable=False, comment="请求方法")
    url: Mapped[str] = mapped_column(String(256), nullable=False, comment="请求URL")
    path_params: Mapped[str | None] = mapped_column(String(1024), nullable=True, comment="路径参数")
    query_params: Mapped[str | None] = mapped_column(String(1024), nullable=True, comment="查询参数")
    response_status: Mapped[int] = mapped_column(Integer, nullable=False, comment="响应状态码")
    content_length: Mapped[int] = mapped_column(Integer, nullable=False, comment="响应内容长度")
    process_time: Mapped[str] = mapped_column(String(32), nullable=False, comment="处理时间")
    req_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="请求ID")