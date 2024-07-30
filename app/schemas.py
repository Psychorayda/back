from typing import Any, List, TypeVar, Union
from pydantic import BaseModel, validator


class BaseSchema(BaseModel):
    '''
    base of all schemas
    '''

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)
RetrieveSchemaType = TypeVar("RetrieveSchemaType", bound=BaseSchema)


######################################################################################################


class PermSchema(BaseSchema):
    '''
    base of perm schema, only have "name" and its validator
    '''
    name: str

    @validator("name", pre=True)
    def onlyAlpha(cls, value):
        if not value.isalpha():
            error_info = cls.__repr_name__ + "name must be alpha only"
            raise ValueError(error_info)
        return value


class PermCreateSchema(PermSchema):
    '''
    schema for create perm
    '''
    desc: str | None = None


class PermUpdateSchema(PermCreateSchema):
    '''
    schema for update perm info
    '''
    id: int


class PermOutSchema(PermUpdateSchema):
    '''
    schema for output perm info
    '''


######################################################################################################


class RoleSchema(BaseSchema):
    '''
    base of role schema, only have "name" and its validator
    '''
    name: str

    @validator("name", pre=True)
    def onlyAlpha(cls, value):
        if not value.isalpha():
            error_info = cls.__repr_name__ + "name must be alpha only"
            raise ValueError(error_info)
        return value
    

class RoleCreateSchema(RoleSchema):
    '''
    schema for create role
    '''
    desc: str | None = None


class RoleUpdateSchema(RoleCreateSchema):
    '''
    schema for update role info
    '''
    id: int


class RoleOutSchema(RoleUpdateSchema):
    '''
    schema for output role info
    '''


class RoleOutWithPermsSchema(RoleUpdateSchema):
    '''
    schema for output role info
    '''
    perms: List[PermOutSchema]


######################################################################################################


class UserSchema(BaseSchema):
    '''
    base of user schema, only have "name" and its validator
    '''
    name: str

    @validator("name", pre=True)
    def onlyAlpha(cls, value):
        if not value.isalpha():
            error_info = cls.__repr_name__ + "name must be alpha only"
            raise ValueError(error_info)
        return value


class UserCreateSchema(UserSchema):
    '''
    schema for create user
    '''
    password: str
    email: str

    @validator("password")
    def length(cls, value):
        if len(value) < 6:
            raise ValueError("length of user password must longer than 6")
        if len(value) > 15:
            raise ValueError("length of user password must shorter than 16")
        return value
    
    @validator("password")
    def haveAlpha(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("user password must have English letters in lowercase & uppercase")
        if not any(char.islower() for char in value):
            raise ValueError("user password must have English letters in lowercase")
        if not any(char.isupper() for char in value):
            raise ValueError("user password must have English letters in uppercase")
        return value

    @validator("password")
    def haveDigit(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("user password must have digit")
        if value.isalpha():
            raise ValueError("user password must have digit")
        return value


class UserUpdateSchema(UserCreateSchema):
    '''
    schema for update user info
    '''
    id: int
    disabled: bool


class UserOutSchema(UserSchema):
    '''
    schema for output user info
    '''
    id: int
    email: str
    disabled: bool


class UserOutWithRolesSchema(UserSchema):
    '''
    schema for output user info
    '''
    id: int
    email: str
    disabled: bool
    roles: List[RoleOutWithPermsSchema]


class UserLoginSchema(UserSchema):
    '''
    schema for user login
    '''
    password: str

    @validator("password")
    def length(cls, value):
        if len(value) < 6:
            raise ValueError("length of user password must longer than 6")
        if len(value) > 15:
            raise ValueError("length of user password must shorter than 16")
        return value
    
    @validator("password")
    def haveAlpha(cls, value):
        if not any(char.isalpha() for char in value):
            raise ValueError("user password must have English letters in lowercase & uppercase")
        if not any(char.islower() for char in value):
            raise ValueError("user password must have English letters in lowercase")
        if not any(char.isupper() for char in value):
            raise ValueError("user password must have English letters in uppercase")
        return value

    @validator("password")
    def haveDigit(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("user password must have digit")
        if value.isalpha():
            raise ValueError("user password must have digit")
        return value
    

######################################################################################################


class UserRoleSchema(BaseSchema):
    '''
    base of user_role schema
    '''


class UserRoleCreateSchema(UserRoleSchema):
    '''
    schema for create user_role
    '''
    user_id: int
    role_id: int


class UserRoleUpdateSchema(UserRoleCreateSchema):
    '''
    schema for update user_role info
    '''
    id: int


class UserRoleOutSchema(UserRoleUpdateSchema):
    '''
    schema for output user_role info
    '''


######################################################################################################


class RolePermSchema(BaseSchema):
    '''
    base of role_perm schema
    '''


class RolePermCreateSchema(RolePermSchema):
    '''
    schema for create role_perm
    '''
    role_id: int
    perm_id: int


class RolePermUpdateSchema(RolePermCreateSchema):
    '''
    schema for update role_perm info
    '''
    id: int


class RolePermOutSchema(RolePermUpdateSchema):
    '''
    schema for output role_perm info
    '''


######################################################################################################


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    
    
class TokenDataSchema(BaseModel):
    user_id: int
    # user_online: UserActiveSchema | None = None


######################################################################################################


class TelesSetSchema(BaseModel):
    peer_name: str
    prop_name: str
    val: Any

class TelesCmdSchema(BaseModel):
    peer_name: str
    command: str